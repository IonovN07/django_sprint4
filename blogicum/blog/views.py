from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
    )
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import ModelFormMixin

from blog.models import Category, Post
from .forms import PostForm


def filter_published(posts = Post.objects.all()):
    return posts.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=timezone.now())


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


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index') 

    def get_object(self, queryset=None):
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])


class PostDeleteView(ModelFormMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index') 

    def get_object(self, queryset=None):
        # Получаем пост по его ID из URL
        return get_object_or_404(filter_published(), id=self.kwargs['post_id'])

    

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


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    paginator = Paginator(filter_published(category.posts), 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'blog/category.html',
        {'category': category,
            'page_obj': page_obj})

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