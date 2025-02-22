from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
    )

from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from django.contrib.auth.models import User
from blog.models import Category, Post
from .forms import PostForm


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
    paginate_by = 3

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=self.author)
        # return filter_published(self.category.posts)

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context







class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user

class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 5 

    def get_queryset(self):
        return filter_published()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index') 

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form) 


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
     
    def get_object(self, queryset=None):
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})

class PostDeleteView(OnlyAuthorMixin, ModelFormMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index') 

    def get_object(self, queryset=None):
        # Получаем пост по его ID из URL
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 3

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        return filter_published(self.category.posts)

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
    




# def category_posts(request, category_slug):
#     category = get_object_or_404(
#         Category,
#         slug=category_slug,
#         is_published=True)
#     paginator = Paginator(filter_published(category.posts), 3)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(
#         request,
#         'blog/category.html',
#         {'category': category,
#             'page_obj': page_obj})    

# def index(request):
#     paginator = Paginator(filter_published(), 5)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(
#         request,
#         'blog/index.html',
#         {'page_obj': page_obj})


# def post_detail(request, post_id):
#     return render(
#         request,
#         'blog/detail.html',
#         {'post': get_object_or_404(filter_published(), id=post_id)})


# def create_post(request):

#     form = PostForm(request.POST or None)
#     context = {'form': form}
#     if form.is_valid():
#         form.save()

#     return render(request, 'blog/create.html', context)

# def post_create_edit(request, post_id=None):
    
#     if post_id is not None:
#         instance = get_object_or_404(Post, id=post_id)
#     else:
#         instance = None
#     form = PostForm(
#         request.POST or None,
#         files=request.FILES or None,
#         instance=instance)
#     context = {'form': form}
#     if form.is_valid():
#         form.save()
#     return render(request, 'blog/create.html', context)

# def delete_post(request, post_id):
    
#     instance = get_object_or_404(Post, id=post_id)
#     form = PostForm(instance=instance)
#     context = {'form': form}
#     if request.method == 'POST':
#         instance.delete()
#         return redirect('blog:index')
#     return render(request, 'blog/create.html', context)