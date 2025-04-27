from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Blog, Review, Comment

class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogapp/blog_detail.html'


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'content', 'image']
    template_name = 'blog_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, f'The Blog has been created successfully!')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})

class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ['title', 'content', 'image']
    template_name = 'blogapp/blog_form.html'

    def form_valid(self, form):
        # Check if image was cleared
        if 'image-clear' in self.request.POST and self.request.POST['image-clear'] == 'on':
            old_instance = Blog.objects.get(pk=self.object.pk)
            if old_instance.image:
                old_instance.image.delete(save=False)

        # Check if image was replaced
        elif 'image' in self.request.FILES:
            old_instance = Blog.objects.get(pk=self.object.pk)
            if old_instance.image:
                old_instance.image.delete(save=False)

        form.instance.last_updated = datetime.now()

        messages.success(self.request, f'The Blog has been updated successfully!')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})

class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog
    template_name = 'blogapp/blog_confirm_delete.html'
    success_url = reverse_lazy('blogapp:blog_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, f'The Blog has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'comment']
    template_name = 'blogapp/review_form.html'

    def form_valid(self, form):
        form.instance.reviewer = self.request.user
        form.instance.blog_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['pk']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'blogapp/comment_form.html'

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        form.instance.review_id = self.kwargs['review_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['blog_pk']})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blogapp:blog_list')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'blogapp/login.html')


def logout_view(request):
    logout(request)
    return redirect('blogapp:blog_list')

def sign_up(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Tu cuenta ha sido creada!')
            return redirect('blogapp:login')
        else:
            messages.error(request, 'Error! Por favor corrige los siguientes errores.')
    else:
        form = UserRegisterForm()
    return render(request, 'blogapp/register.html', {'form':form})