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

""" How book author suggested doing a searching system.
    If it's more optimized or more "Django/Pythonic", let me know in commit comment.
    
def post_search(request):
   form = SearchForm()
   query = None
   results = []
   if 'query' in request.GET:
       form = SearchForm(request.GET)
       if form.is_valid():
           query = form.cleaned_data['query']
           search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
           search_query = SearchQuery(query)
           results = Post.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)
           ).filter(rank_gte=0.3).order_by('-rank')
   return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results}) """


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    paginated_by = 10
    tag = None
    query = None

    if request.method == "POST":
        to_delete_post = request.POST.get('to-delete-post')
        to_delete_comment = request.POST.get('to-delete-comment')
        search_form = SearchForm(request.POST)
        post_form = PostForm(request.POST)
        tag_form = TagForm(request.POST)
        comment_form = CommentForm(request.POST)

        """ How I did my search system. I think it's too over forced,
            to make additional view function just to filter queryset. """
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            object_list = Post.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')

        if comment_form.is_valid():
            post_id = comment_form.data["id"]
            new_comment = comment_form.save(commit=False)
            post = get_object_or_404(Post, id=post_id)
            new_comment.post = post
            new_comment.save()
            return HttpResponseRedirect(reverse("blog:post_list"))

        if tag_form.is_valid():
            new_tag = tag_form.save(commit=False)
            new_tag.slug = slugify(new_tag.name)
            new_tag.save()
            return HttpResponseRedirect(reverse("blog:post_list"))

        if post_form.is_valid():
            new_post = post_form.save(commit=False)
            new_post.slug = slugify(new_post.title)
            new_post.author = User.objects.get(pk=1)
            new_post.status = 'published'
            new_post.save()
            post_form.save_m2m()
            return HttpResponseRedirect(reverse("blog:post_list"))

        if to_delete_post:
            post = Post.published.get(pk=to_delete_post)
            post.delete()
            return HttpResponseRedirect(reverse("blog:post_list"))

        if to_delete_comment:
            comment = Comment.is_active.get(pk=to_delete_comment)
            comment.delete()
            return HttpResponseRedirect(reverse("blog:post_list"))

    else:
        comment_form = CommentForm()
        post_form = PostForm()
        tag_form = TagForm()
        search_form = SearchForm()

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
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag,
                                                   'comment_form': comment_form, 'post_form': post_form,
                                                   'tag_form': tag_form, 'search_form': search_form, 'query': query})


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
