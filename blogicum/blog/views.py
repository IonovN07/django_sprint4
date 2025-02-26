from django import forms
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
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

POSTS_PER_PAGE = 10

def filter_published(posts=Post.objects.all()):
    return posts.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=timezone.now())


class AuthorPostMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not ( self.object.author == request.user):
            return redirect(
                reverse('blog:post_detail', args=[self.object.id])
            )
        return super().dispatch(request, *args, **kwargs)


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile', args=[self.object.author.username])


class UserDetailView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return author.posts.annotate(comment_count=Count('comments')).order_by('-pub_date')

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
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        return (
            reverse(
                'blog:profile',
                kwargs={'username': self.object.username})
        )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE
    queryset = (
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
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )


class PostUpdateView(AuthorPostMixin, PostMixin, UpdateView):

    def get_object(self, queryset=None):
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])


class PostDeleteView(AuthorPostMixin, PostMixin, ModelFormMixin, DeleteView):

    def get_object(self, queryset=None):
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE

    def get_category(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return category

    def get_queryset(self):
        category = self.get_category()
        return (
            filter_published(category.posts)
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )

    def get_context_data(self, object_list=None, **kwargs):
        return super().get_context_data(**kwargs, category=self.get_category())


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id' 

    # def get_object(self, queryset=None):
    #     comment_id = self.kwargs.get('comment_id')
    #     return get_object_or_404(Comment, id=comment_id)

    def get_context_data(self, **kwargs):
        return (
            super().get_context_data(**kwargs, post_id=self.kwargs['post_id'])
        )

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            raise PermissionDenied(
                reverse( 'blog:post_detail', args=[self.kwargs['post_id']])
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.kwargs['post_id']]
        )


# class AuthorCommentMixin(LoginRequiredMixin):

#     def dispatch(self, request, *args, **kwargs):
#         comment = self.get_object()
#         if comment.author != request.user:
#             raise PermissionDenied(
#                 reverse( 'blog:post_detail', args=[self.kwargs['post_id']])
#             )
#         return super().dispatch(request, *args, **kwargs)


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
    # model = Comment
    # form_class = CommentForm
    # template_name = 'blog/comment.html'
    # pk_url_kwarg = 'comment_id' 

    # # def get_object(self, queryset=None):
    # #     comment_id = self.kwargs.get('comment_id')
    # #     return get_object_or_404(Comment, id=comment_id)

    # def get_context_data(self, **kwargs):
    #     return (
    #         super().get_context_data(**kwargs, post_id=self.kwargs['post_id'])
    #     )


class CommentDeleteView(CommentMixin, DeleteView):
        pass
    # model = Comment
    # template_name = 'blog/comment.html'
    # pk_url_kwarg = 'comment_id'
    

    # # def get_object(self, queryset=None):
    # #     return get_object_or_404(
    # #         Comment, 
    # #         id=self.kwargs['comment_id'],
    # #         post_id=self.kwargs['post_id']
    # #     )

    # def get_context_data(self, **kwargs):
    #     return (
    #         super().get_context_data(**kwargs, post_id=self.kwargs['post_id'])
    #     )
