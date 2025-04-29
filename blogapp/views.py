from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Blog, Review, Comment
from django.contrib.messages import get_messages

class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogapp/blog_detail.html'


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'content']
    template_name = 'blog_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})



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
    storage = get_messages(request)
    for message in storage:
        pass 

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
            messages.error(request, 'ERROR! Verifica nuevamente tu información')
    else:
        form = UserRegisterForm()
    return render(request, 'blogapp/register.html', {
        'form':form,
        'errors': form.errors.get_json_data() if request.method == 'POST' else None
    })

def facebook_register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('social:begin', backend='facebook') 
    else:
        form = UserRegisterForm()
    return render(request, 'blogapp/register.html', {'form': form})

def social_auth_error(request):
    error = request.GET.get('error', None)
    error_description = request.GET.get('error_description', '')
    
    if error == 'access_denied' or 'user_denied' in error_description:
        messages.info(request, 'Has cancelado el inicio de sesión con tu cuenta')
        return redirect('blogapp:login')
    
    messages.error(request, 'Ocurrió un error durante la autenticación. Por favor, intenta nuevamente.')
    return redirect('blogapp:login')
