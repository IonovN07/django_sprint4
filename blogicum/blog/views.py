from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.edit import ModelFormMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

from blog.models import Category, Post, Comment
from .forms import PostForm, CommentForm
from django import forms


def filter_published(posts = Post.objects.all()):
    return posts.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=timezone.now())

class UserDetailView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        self.author = get_object_or_404(
            User, 
            username=self.kwargs['username']
            )
        return super().get_queryset().order_by('-pub_date').filter(
            author=self.author
        ).annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'

    class EditProfileForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name']

    def get_form_class(self):
        return self.EditProfileForm

    def get_object(self, queryset=None):
        self.author = get_object_or_404(
            User, 
            username=self.kwargs['username']
            )
        return self.author

    def get_success_url(self):
        return (
            reverse_lazy(
                'blog:profile', 
                kwargs={'username': self.object.username})
            )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.author.username 
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            filter_published()
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
            )


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if post.author == self.request.user or filter_published():
            return post
        return get_object_or_404(Post, pk=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context 


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form) 

    def get_success_url(self):
        username = self.object.author.username
        return reverse('blog:profile', args=[username])


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not (
            request.user.is_authenticated 
            and self.object.author == request.user
            ):
            return redirect(
                reverse('blog:post_detail', kwargs={'post_id': self.object.id})
            )
        return super().dispatch(request, *args, **kwargs)
     
    def get_object(self, queryset=None):
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(LoginRequiredMixin, ModelFormMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not (
            request.user.is_authenticated 
            and self.object.author == request.user
            ):
            return redirect(
                reverse('blog:post_detail', kwargs={'post_id': self.object.id})
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])

    def get_success_url(self):
        username = self.object.author.username
        return reverse('blog:profile', args=[username])


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'], 
            is_published=True
            )
        return ( 
            filter_published(self.category.posts)
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments')) 
            )

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
    

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise PermissionDenied(
                'Вы не авторизованы для редактирования этого комментария.'
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.kwargs.get('post_id')
        return context

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            raise PermissionDenied(
                'Вы не авторизованы для удаления этого комментария.'
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, id=comment_id, post_id=post_id)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('blog:post_detail', kwargs={'post_id': post_id})
