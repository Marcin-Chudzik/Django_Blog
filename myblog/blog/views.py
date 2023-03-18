from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.shortcuts import reverse
from django.template.defaultfilters import slugify
from taggit.models import Tag
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from .forms import EmailPostForm, CommentForm, PostForm, TagForm, SearchForm
from .models import Post, Comment


def post_list(request, tag_slug=None):
    """
        View function that displays a list of published blog posts.

        :param request: HttpRequest object representing the incoming request
        :param tag_slug: optional string representing the slug of a tag to filter posts by
        :return: HttpResponse object representing the server's response

        This view function retrieves a list of published blog posts from the database
        using the `published` manager of the `Post` model. It then optionally filters
        the list by a specified tag, if `tag_slug` is provided.

        The view function uses the `Paginator` class from Django's built-in pagination
        framework to split the list of posts into pages. The number of posts per page is
        set by the `paginated_by` variable, which is currently set to 10.

        If the incoming request is a POST request, the view function processes any
        submitted forms included in the request. The function checks for several
        specific form names and performs different actions based on the form name.

        The view function supports the following forms:

        - `CommentForm`: Allows users to add comments to blog posts. If a valid `CommentForm`
          is submitted, the function adds the comment to the corresponding post and
          redirects to the `post_list` view.
        - `TagForm`: Allows users to add new tags to blog posts. If a valid `TagForm`
          is submitted, the function adds the new tag to the database and redirects to
          the `post_list` view.
        - `PostForm`: Allows users to create new blog posts. If a valid `PostForm` is
          submitted, the function creates a new `Post` object in the database and
          redirects to the `post_list` view.
        - `SearchForm`: Allows users to search for posts by keyword. If a valid
          `SearchForm` is submitted, the function performs a database query to find
          posts that match the search query and displays them on the page.

        If the incoming request contains a `to-delete-post` or `to-delete-comment`
        parameter in the POST data, the function deletes the corresponding post or
        comment from the database and redirects to the `post_list` view.

        The function also includes several context variables that are passed to the
        template for rendering, including:

        - `page`: The current page number of the paginated post list
        - `posts`: The current page of posts to display
        - `tag`: The tag object to filter posts by (if any)
        - `forms`: A dictionary of form objects to include on the page
        - `query`: The search query string (if any)

        The function uses the `render` shortcut to render the `list.html` template and
        pass the context variables to it.
    """
    object_list = Post.published.all()
    paginated_by = 10
    tag = None
    query = None
    forms = {
        'comment_form': CommentForm,
        'post_form': PostForm,
        'tag_form': TagForm,
        'search_form': SearchForm,
    }

    if request.method == "POST":
        to_delete_post = request.POST.get('to-delete-post', None)
        to_delete_comment = request.POST.get('to-delete-comment', None)

        for form_name, form_class in forms.items():
            forms[form_name] = form_class(request.POST)
            if forms[form_name].is_valid():
                if form_name == 'search_form':
                    query = forms[form_name].cleaned_data['query']
                    search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
                    search_query = SearchQuery(query)
                    object_list = Post.objects.annotate(
                        search=search_vector,
                        rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3) \
                        .order_by('-rank')

                elif form_name == 'comment_form':
                    post_id = forms[form_name].data['id']
                    post = get_object_or_404(Post, id=post_id)
                    forms[form_name].save(commit=False).post = post
                    forms[form_name].save()
                    return HttpResponseRedirect(reverse('blog:post_list'))

                elif form_name == 'tag_form':
                    new_tag = forms[form_name].save(commit=False)
                    new_tag.slug = slugify(new_tag.name)
                    new_tag.save()
                    return HttpResponseRedirect(reverse('blog:post_list'))

                elif form_name == 'post_form':
                    new_post = forms[form_name].save(commit=False)
                    new_post.slug = slugify(new_post.title)
                    new_post.author = User.objects.get(pk=1)
                    new_post.status = 'published'
                    new_post.save()
                    forms[form_name].save_m2m()
                    return HttpResponseRedirect(reverse('blog:post_list'))

        if to_delete_post:
            post = Post.published.get(pk=to_delete_post)
            post.delete()
            return HttpResponseRedirect(reverse('blog:post_list'))

        if to_delete_comment:
            comment = Comment.is_active.get(pk=to_delete_comment)
            comment.delete()
            return HttpResponseRedirect(reverse('blog:post_list'))

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, paginated_by)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'page': page,
        'posts': posts,
        'tag': tag,
        'forms': forms,
        'query': query
    }

    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    sent = False

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        share_form = EmailPostForm(request.POST)
        to_delete_comment = request.POST.get("to-delete-comment")

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return HttpResponseRedirect(reverse('blog:post_detail',
                                                args=[year, month, day, post.slug]))

        if share_form.is_valid():
            data = share_form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{data["name"]} ({data["email"]} encourage to read "{post.title}"'
            message = f'Read post "{post.title}" on page {post_url}' \
                      f'Comment added by {data["name"]}: {data["comments"]}.'
            send_mail(subject, message, 'admin@myblog.com', (data['to'],))
            sent = True
            share_form = EmailPostForm()
            return render(request, 'blog/post/detail.html',
                          {'post': post, 'comments': comments, 'comment_form': comment_form,
                           'share_form': share_form, 'similar_posts': similar_posts, 'sent': sent})

        if to_delete_comment:
            comment = Comment.is_active.get(pk=to_delete_comment)
            comment.delete()
            return render(request, 'blog/post/detail.html',
                          {'post': post, 'comments': comments, 'comment_form': comment_form,
                           'share_form': share_form, 'similar_posts': similar_posts, 'sent': sent})

    else:
        comment_form = CommentForm()
        share_form = EmailPostForm()

    return render(request, 'blog/post/detail.html',
                  {'post': post, 'comments': comments, 'comment_form': comment_form,
                   'share_form': share_form, 'similar_posts': similar_posts})
