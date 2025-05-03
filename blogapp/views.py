from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, RedirectView
from django.urls import reverse_lazy
from .models import Blog, Review, Comment, UserProfile
from django.contrib.messages import get_messages
from social_core.exceptions import AuthCanceled, AuthForbidden


class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'blogapp/profile_user.html'

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            # Create a profile if it doesn't exist
            return UserProfile.objects.create(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogs'] = Blog.objects.filter(author=self.request.user).select_related('author')
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['profile_photo', 'bio', 'location', 'birth_date', 'interests']
    template_name = 'blogapp/profile_form.html'

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            # Create a profile if it doesn't exist
            return UserProfile.objects.create(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:profile', kwargs={'pk': self.request.user.profile.pk})

#TODO: fix the delete view to delete the user and profile
class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = UserProfile
    template_name = 'blogapp/profile_confirm_delete.html'
    success_url = reverse_lazy('blogapp:blog_list')

    def get_object(self, *args, **kwargs):
        # Retrieve by user relationship
        return self.request.user.profile

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        response = super().delete(request, *args, **kwargs)
        logout(request)  # Log the user out
        user.delete()  # Delete the user (cascade will delete profile)
        messages.success(request, 'Your profile has been deleted successfully!')
        return redirect('blogapp:blog_list')  # Redirect after deletion

class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 10

    def get_queryset(self):
        return Blog.objects.select_related('author').prefetch_related('reviews').order_by('-created_at')


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogapp/blog_detail.html'
    context_object_name = 'blog'

    def get_queryset(self):
        return super().get_queryset().select_related('author').prefetch_related('reviews__comments')


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'content', 'image']
    template_name = 'blogapp/blog_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'The Blog has been created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ['title', 'content', 'image']
    template_name = 'blogapp/blog_form.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            messages.error(request, "You don't have permission to edit this blog.")
            return redirect('blogapp:blog_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Handle image deletion/replacement
        if 'image-clear' in self.request.POST and self.request.POST['image-clear'] == 'on':
            if self.object.image:
                self.object.image.delete(save=False)
        elif 'image' in self.request.FILES and self.object.image:
            self.object.image.delete(save=False)

        form.instance.last_updated = datetime.now()
        messages.success(self.request, 'The Blog has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog
    template_name = 'blogapp/blog_confirm_delete.html'
    success_url = reverse_lazy('blogapp:blog_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            messages.error(request, "You don't have permission to delete this blog.")
            return redirect('blogapp:blog_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        blog = self.get_object()
        # Delete associated image file if exists
        if blog.image:
            blog.image.delete(save=False)
        messages.success(request, 'The Blog has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'comment']
    template_name = 'blogapp/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = Blog.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.reviewer = self.request.user
        form.instance.blog_id = self.kwargs['pk']
        messages.success(self.request, 'Your review has been posted successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['pk']})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'blogapp/comment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review'] = Review.objects.get(pk=self.kwargs['review_pk'])
        return context

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        form.instance.review_id = self.kwargs['review_pk']
        messages.success(self.request, 'Your comment has been posted successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['blog_pk']})


class LoginView(FormView):
    template_name = 'blogapp/login.html'
    success_url = reverse_lazy('blogapp:blog_list')

    def form_valid(self, form):
        username = form.cleaned_data.get('username', '')
        password = form.cleaned_data.get('password', '')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            next_url = self.request.GET.get('next', self.get_success_url())
            return redirect(next_url)

        messages.error(self.request, 'Invalid username or password')
        return self.form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blogapp:blog_list')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        # Return a basic form without a form class
        if self.request.method == 'POST':
            return {'username': self.request.POST.get('username', ''), 
                   'password': self.request.POST.get('password', '')}
        return {}


class LogoutView(RedirectView):
    url = reverse_lazy('blogapp:blog_list')
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been logged out successfully')
        return super().get(request, *args, **kwargs)


class SignUpView(FormView):
    template_name = 'blogapp/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('blogapp:login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Your account has been created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['errors'] = self.get_form().errors.get_json_data() if self.request.method == 'POST' else None
        return context
        
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blogapp:blog_list')
        return super().dispatch(request, *args, **kwargs)
