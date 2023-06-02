from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.shortcuts import reverse
from django.template.defaultfilters import slugify
from taggit.models import Tag
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
)
from .forms import (
    EmailPostForm,
    CommentForm,
    PostForm,
    TagForm,
    SearchForm,
)
from .models import (
    Post,
    Comment,
)


def post_list(request, tag_slug: str = None):
    """
        View function that displays a list of published blog posts.
        Optionally filtered by a provided tag.
        Includes paginator to split the list of posts into pages.
        Performs different actions based on the incoming form and parameters.

        :param tag_slug: Representing the slug of a tag to filter posts by.

        The function includes several context variables that are passed to the
        template for rendering, including:

        - `page`: The current page number of the paginated post list
        - `posts`: The current page of posts to display
        - `tag`: The tag object to filter posts by (if any)
        - `forms`: A dictionary of form objects to include on the page
        - `query`: The search query string (if any)
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

    if request.method == 'POST':
        to_delete_post = request.POST.get('to-delete-post', None)
        to_delete_comment = request.POST.get('to-delete-comment', None)

        for form_name, form_class in forms.items():
            forms[form_name] = form_class(request.POST)

            if forms[form_name].is_valid():
                if form_name == 'search_form':
                    """Filter database query by submitted keyword."""
                    query = forms[form_name].cleaned_data['query']
                    search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
                    search_query = SearchQuery(query)
                    object_list = Post.objects.annotate(
                        search=search_vector,
                        rank=SearchRank(search_vector, search_query)
                        ).filter(rank__gte=0.3).order_by('-rank')

                elif form_name == 'comment_form':
                    """Create and add new comment to the post, then redirect to the post-list view."""
                    post_id = request.POST.get('post-id', None)

                    if post_id:
                        post = get_object_or_404(Post, id=post_id)
                        forms[form_name].save(commit=False)
                        forms[form_name].post = post
                        forms[form_name].save()
                    return HttpResponseRedirect(reverse('blog:post-list'))

                elif form_name == 'tag_form':
                    """Create a new tag and redirect to the post-list view."""
                    new_tag = forms[form_name].save(commit=False)
                    new_tag.slug = slugify(new_tag.name)
                    new_tag.save()
                    return HttpResponseRedirect(reverse('blog:post-list'))

                elif form_name == 'post_form':
                    """Create a new post and redirect to the post-list view."""
                    new_post = forms[form_name].save(commit=False)
                    new_post.slug = slugify(new_post.title)
                    new_post.author = User.objects.get(pk=1)
                    new_post.status = 'published'
                    new_post.save()
                    forms[form_name].save_m2m()
                    return HttpResponseRedirect(reverse('blog:post-list'))

        if to_delete_post:
            """Delete corresponding post."""
            Post.published.get(pk=to_delete_post).delete()
            return HttpResponseRedirect(reverse('blog:post-list'))

        if to_delete_comment:
            """Delete corresponding comment."""
            Comment.is_active.get(pk=to_delete_comment).delete()
            return HttpResponseRedirect(reverse('blog:post-list'))

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


def post_detail(request, year: str, month: str, day: str, post_slug: str):
    """
    View function that displays the detail page for a single blog post with related comments.
    Performs different actions based on the incoming form.
    Shows similar posts which contain the biggest number of shared tags with displayed post
    followed by the publication date.

    :params year, month, day: Strings representing the year, month and day of the post's publication date.
    :param post_slug: string representing the slug of the post to display.

    The function also includes several context variables that are passed to the template for rendering, including:
    - `post`: The blog post to display.
    - `comments`: The comments associated with the post.
    - `forms`: A dictionary of form objects to include on the page.
    - `similar_posts`: A list of similar posts based on shared tags.
    - `sent`: A boolean indicating whether an email was successfully sent.
    """
    post = get_object_or_404(Post,
                             slug=post_slug,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
        .exclude(id=post.id)\
        .annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]
    sent = False
    forms = {
        'comment_form': CommentForm,
        'share_form': EmailPostForm,
    }
    context = {
        'post': post,
        'comments': comments,
        'forms': forms,
        'similar_posts': similar_posts,
        'sent': sent,
    }

    if request.method == 'POST':
        to_delete_comment = request.POST.get('to-delete-comment', None)

        for form_name, form_class in forms.items():
            forms[form_name] = form_class(request.POST)

            if forms[form_name].is_valid():
                if form_name == 'comment_form':
                    """Create and add new comment to the actual displayed post."""
                    new_comment = forms[form_name].save(commit=False)
                    new_comment.post = post
                    new_comment.save()

                    return HttpResponseRedirect(reverse('blog:post-detail', args=[year, month, day, post.slug]))

                elif form_name == 'share_form':
                    """Send an email message contains a link to the actual displayed post with short message."""
                    data = forms[form_name].cleaned_data
                    post_url = request.build_absolute_uri(post.get_absolute_url())

                    subject = f'{data["name"]} ({data["email"]} encourage to read "{post.title}"'
                    message = f'Read post "{post.title}" on page {post_url}' \
                              f'Comment added by {data["name"]}: {data["comments"]}.'

                    send_mail(subject, message, 'admin@myblog.com', (data['to'],))
                    context['sent'] = True
                    forms[form_name] = EmailPostForm()

                    return render(request, 'blog/post/detail.html', context)

        if to_delete_comment:
            """Delete a corresponding comment."""
            Comment.is_active.get(pk=to_delete_comment).delete()
            return render(request, 'blog/post/detail.html', context)

    return render(request, 'blog/post/detail.html', context)
