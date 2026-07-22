from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Post
from .permissions import StaffOrBenegnadorRequiredMixin, is_staff_or_benegnador


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_manage_blog'] = is_staff_or_benegnador(self.request.user)
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            if is_staff_or_benegnador(self.request.user):
                return Post.objects.all()
        return Post.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_manage_blog'] = is_staff_or_benegnador(self.request.user)
        return context


class PostCreateView(StaffOrBenegnadorRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'cover_image', 'content', 'is_published']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Artigo publicado com sucesso!")
        return super().form_valid(form)


class PostUpdateView(StaffOrBenegnadorRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'cover_image', 'content', 'is_published']
    template_name = 'blog/post_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:post_list')

    def form_valid(self, form):
        messages.success(self.request, "Artigo atualizado com sucesso!")
        return super().form_valid(form)


class PostDeleteView(StaffOrBenegnadorRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:post_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Artigo removido com sucesso!")
        return super().delete(request, *args, **kwargs)
