from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import paginator


def index(request):
    path = 'posts/index.html'

    posts = Post.objects.all().order_by('-pub_date')

    page_obj = paginator(request, posts)

    main_page = True
    context = {
        'page_obj': page_obj,
        'main_page': main_page
    }
    return render(request, path, context)


def group_posts(request, slug):
    path = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by('-pub_date')

    page_obj = paginator(request, posts)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, path, context)


def profile(request, username):
    path = 'posts/profile.html'

    author = get_object_or_404(User, username=username)

    num_of_posts = Post.objects.filter(author=author).count()

    posts = Post.objects.filter(author=author).order_by('-pub_date')

    page_obj = paginator(request, posts)

    try:
        follow = Follow.objects.get(
            user=request.user,
            author=author
        )
    except Exception:
        follow = False

    following = False
    if follow:
        following = True

    context = {
        'author': author,
        'num_of_posts': num_of_posts,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, path, context)


def post_detail(request, post_id):
    path = 'posts/post_detail.html'

    form = CommentForm(request.POST or None)

    post = get_object_or_404(Post, pk=post_id)

    comments = Comment.objects.filter(post=post).order_by('-created')

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, path, context)


@login_required
def post_create(request):
    path = 'posts/create_post.html'

    form = PostForm(request.POST or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', request.user)

    form = PostForm()

    context = {'form': form}
    return render(request, path, context)


@login_required
def post_edit(request, post_id):
    path = 'posts/create_post.html'

    is_edit = True

    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()

        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit
    }
    return render(request, path, context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(id=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def followings_posts(request):
    path = 'posts/followings.html'

    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author').order_by('-pub_date')

    page_obj = paginator(request, posts)

    followings = True
    context = {
        'page_obj': page_obj,
        'followings': followings
    }
    return render(request, path, context)


@login_required
def author_follow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.create(
        user=request.user,
        author=author
    )
    return redirect('posts:profile', username=username)


@login_required
def author_unfollow(request, username):
    author = User.objects.get(username=username)
    follow_to_be_deleted = Follow.objects.get(
        user=request.user,
        author=author
    )
    follow_to_be_deleted.delete()
    return redirect('posts:profile', username=username)