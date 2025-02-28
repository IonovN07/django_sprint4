from django import forms
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.edit import ModelFormMixin

from blog.models import Category, Post, Comment
from .forms import PostForm, CommentForm

from django.http import Http404

POSTS_PER_PAGE = 10


def filter_published(
        posts=Post.objects.all(),
        filter_published=True,
        select_related=True,
        annotate=True):
    if select_related:
        posts = posts.select_related('category', 'location', 'author')
    if annotate:
        posts = (
            posts
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )
    if filter_published:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=timezone.now()
        )

    return posts


class AuthorPostMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        if not (object.author == request.user):
            return redirect(
                reverse('blog:post_detail', args=[object.id])
            )
        return super().dispatch(request, *args, **kwargs)


class UserDetailView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return filter_published(author.posts, filter_published=False)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            profile=get_object_or_404(User, username=self.kwargs['username'])
        )


class EditProfileView(LoginRequiredMixin, UpdateView):

    class EditProfileForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name']

    form_class = EditProfileForm
    model = User
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user])


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE
    queryset = filter_published()



class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'


    def get_object(self, queryset=None):
        post = get_object_or_404(
            super().get_queryset(),
            id=self.kwargs['post_id']
        )
        if post.author == self.request.user:
            return post
        if post.is_published and post.pub_date < timezone.now():
            return post
        raise Http404("Post not found or you don't have permission to view this post")    
        
        # return filter_published(annotate=False, select_related=False)
            

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        
        context['comments'] = self.get_object().comments.select_related('author')
        return context

    # def get_context_data(self, **kwargs):
    #     return super().get_context_data(
    #         **kwargs,
    #         form=CommentForm(),
    #         if self.object:
    #         comments=self.object.comments.select_related('author')
    #     )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:profile', args=[self.object.author.username])


class PostUpdateView(AuthorPostMixin, PostMixin, UpdateView):
    pass


class PostDeleteView(AuthorPostMixin, PostMixin, ModelFormMixin, DeleteView):
    pass


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return filter_published(self.get_category().posts)

    def get_context_data(self, object_list=None, **kwargs):
        return super().get_context_data(**kwargs, category=self.get_category())


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_context_data(self, **kwargs):
        return (
            super().get_context_data(**kwargs, post=self.get_object())
        )

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            raise PermissionDenied(
                reverse('blog:post_detail', args=[self.kwargs['post_id']])
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.kwargs['post_id']]
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.kwargs['post_id']]
        )


class CommentEditView(CommentMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, DeleteView):
    pass
