from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, RedirectView
from django.urls import reverse_lazy
from .models import Blog, Review, Comment, UserProfile
from django.contrib.messages import get_messages
from social_core.exceptions import AuthCanceled, AuthForbidden
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django import forms
from django.db.models import Avg, Count, Q
from django.contrib.auth.forms import UserCreationForm
from random import choice
from django.shortcuts import redirect



def get_location_info(location_code):
    LOCATION_MAP = {
        'BOC': {'flag_url': 'Bocas_del_Toro', 'name': 'Bocas del Toro', 'color': 'lime'},
        'CHI': {'flag_url': 'Chiriqui', 'name': 'Chiriquí', 'color': 'green'},
        'COC': {'flag_url': 'Cocle', 'name': 'Coclé', 'color': 'amber'},
        'COL': {'flag_url': 'Colon', 'name': 'Colón', 'color': 'indigo'},
        'DAR': {'flag_url': 'Darien', 'name': 'Darién', 'color': 'cyan'},
        'HER': {'flag_url': 'Herrera', 'name': 'Herrera', 'color': 'yellow'},
        'LOS': {'flag_url': 'Los_Santos', 'name': 'Los Santos', 'color': 'orange'},
        'PAN': {'flag_url': 'Panama', 'name': 'Panamá', 'color': 'red'},
        'POE': {'flag_url': 'Panama_Oeste', 'name': 'Panamá Oeste', 'color': 'emerald'},
        'VER': {'flag_url': 'Veraguas', 'name': 'Veraguas', 'color': 'blue'},
    }
    return LOCATION_MAP.get(location_code)

class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'blogapp/profile_user.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        try:
            username = self.kwargs.get('username')
            user = get_user_model().objects.get(username=username)

            try:
                return user.profile
            except UserProfile.DoesNotExist:
                if user == self.request.user:
                    return UserProfile.objects.create(user=user)
                return None
        except get_user_model().DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            viewed_user = get_user_model().objects.get(username=self.kwargs.get('username'))
            profile = self.get_object()

            # Basic user info
            context['profile_user'] = viewed_user

            # Profile info
            context['interests_list'] = profile.interests if profile and profile.interests else []
            context['location_info'] = get_location_info(profile.location if profile else None)

            # Blogs by the user
            user_blogs = Blog.objects.filter(author=viewed_user).select_related('author')
            context['blogs'] = user_blogs
            context['blogs_count'] = user_blogs.count()

            # Blog ratings
            blog_ids = [blog.id for blog in user_blogs]
            ratings = Review.objects.filter(blog_id__in=blog_ids).values('blog_id').annotate(
                avg_rating=Avg('rating'),
                review_count=Count('id')
            )

            # Calculate average rating for user's blogs
            if ratings:
                valid_ratings = [item['avg_rating'] for item in ratings if item['avg_rating']]
                average_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0
                context['average_rating'] = round(average_rating, 1) if average_rating else 0
            else:
                context['average_rating'] = 0

            # Reviews by the user
            user_reviews = Review.objects.filter(reviewer=viewed_user)
            context['reviews_list'] = user_reviews
            context['reviews_count'] = user_reviews.count()
            context['reviewed_blogs'] = [review.blog for review in user_reviews]

            # Average rating given by user in reviews
            if user_reviews:
                avg_review_rating = sum(review.rating for review in user_reviews) / user_reviews.count()
                context['average_review_rating'] = round(avg_review_rating, 1) if avg_review_rating else 0
            else:
                context['average_review_rating'] = 0

            # Comments by the user
            user_comments = Comment.objects.filter(commenter=viewed_user)
            context['comments_list'] = user_comments
            context['comments_count'] = user_comments.count()
            context['commented_blogs'] = [comment.review.blog for comment in user_comments]

            # Tags used by the user
            all_tags = set()
            for blog in user_blogs:
                if blog.tags:
                    blog_tags = blog.tags if isinstance(blog.tags, list) else []
                    all_tags.update(blog_tags)
            context['tags_collection'] = sorted(list(all_tags))
            context['tags_count'] = len(context['tags_collection'])

        except get_user_model().DoesNotExist:
            context['profile_user'] = None
            context['blogs'] = []
            context['interests_list'] = []
            context['location_info'] = get_location_info(None)
            context['blogs_count'] = 0
            context['reviews_count'] = 0
            context['comments_count'] = 0
            context['average_rating'] = 0
            context['average_review_rating'] = 0
            context['tags_collection'] = []
            context['tags_count'] = 0

        return context

    def render_to_response(self, context, **response_kwargs):
        # Si el usuario no existe, redirigir a la lista de blogs con un error
        if not context.get('profile_user'):
            messages.error(self.request, "Usuario no encontrado.")
            return redirect('blogapp:blog_list')
        return super().render_to_response(context, **response_kwargs)

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
        messages.success(self.request, '¡Tu perfil ha sido actualizado exitosamente!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:profile', kwargs={'username': self.request.user.username})

class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = UserProfile
    template_name = 'blogapp/profile_confirm_delete.html'
    success_url = reverse_lazy('blogapp:blog_list')

    def get_object(self, queryset=None):
        try:
            profile = self.request.user.profile
            return profile
        except UserProfile.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            messages.error(request, "Profile not found.")
            return redirect('blogapp:blog_list')

        user = self.request.user

        # Delete profile photo if exists
        if self.object.profile_photo:
            self.object.profile_photo.delete(save=False)

        # Store session key before user deletion
        session_key = request.session.session_key

        user.delete()

        # Clear the session
        if session_key:
            print(f"Clearing session: {session_key}")
            Session.objects.filter(session_key=session_key).delete()
            print("Session cleared")

        messages.success(request, '¡Tu perfil ha sido eliminado exitosamente!')
        return redirect('blogapp:blog_list')

class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 10
    random_blog_id = None

    def dispatch(self, request, *args, **kwargs):
        if request.GET.get('sort') == 'random':
            self.get_queryset()
            if hasattr(self, 'random_blog_id') and self.random_blog_id:
                return redirect('blogapp:blog_detail', pk=self.random_blog_id)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Blog.objects.select_related('author', 'author__profile').prefetch_related('reviews')
        sort = self.request.GET.get('sort', 'latest')

        if sort == 'most_commented':
            queryset = queryset.annotate(
                comment_count=Count('reviews__comments')
            ).order_by('-comment_count', '-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'best_rated':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating', '-created_at')
        elif sort == 'random':
            blog_ids = Blog.objects.values_list('id', flat=True)
            if blog_ids:
                random_id = choice(list(blog_ids))
                self.random_blog_id = random_id
                queryset = queryset.filter(id=random_id)
            else:
                queryset = queryset.none()
        else:  # default: latest
            queryset = queryset.order_by('-created_at')

        return self._apply_filters(queryset)

    def _apply_filters(self, queryset):
        """Apply all filters from request parameters to the queryset."""
        filters = {}

        # Filter by tag
        tag = self.request.GET.get('tag', '').strip()
        if tag:
            queryset = queryset.filter(Q(tags__icontains=tag))

        # Filter by author username
        author = self.request.GET.get('author', '').strip()
        if author:
            filters['author__username'] = author

        # Filter by province/location
        location = (self.request.GET.get('province') or self.request.GET.get('location', '')).strip()
        if location:
            filters['author__profile__location'] = location

        # Filter by date range
        try:
            date_from = self.request.GET.get('date_from', '').strip()
            if date_from:
                filters['created_at__gte'] = date_from

            date_to = self.request.GET.get('date_to', '').strip()
            if date_to:
                filters['created_at__lte'] = date_to
        except (ValueError, TypeError):
            pass  # Ignore invalid date formats

        # Apply collected filters
        if filters:
            queryset = queryset.filter(**filters)

        # Search in title and content
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """Enhance context with blog metadata for rendering."""
        context = super().get_context_data(**kwargs)
        blogs_list = []
        all_tags = set()

        if not context['blogs']:
            context['blogs_list'] = []
            context['tags_collection'] = []
            return context

        # Get blog IDs for batch operations
        blog_ids = [blog.id for blog in context['blogs']]

        # Batch query for ratings and comments
        ratings_dict = self._get_ratings_dict(blog_ids)
        comments_dict = self._get_comments_dict(blog_ids)

        # Process each blog
        for blog in context['blogs']:
            blog_data = self._prepare_blog_data(blog, ratings_dict, comments_dict)
            blogs_list.append(blog_data)

            # Collect tags for all blogs
            if blog.tags and isinstance(blog.tags, list):
                all_tags.update(blog.tags)

        context['blogs_list'] = blogs_list
        context['tags_collection'] = sorted(list(all_tags))

        return context

    def _get_ratings_dict(self, blog_ids):
        """Get average ratings and review counts for blogs."""
        ratings = Review.objects.filter(blog_id__in=blog_ids).values('blog_id').annotate(
            avg_rating=Avg('rating'),
            review_count=Count('id')
        )

        return {item['blog_id']: {
            'avg_rating': round(item['avg_rating'], 1) if item['avg_rating'] else 0,
            'review_count': item['review_count']
        } for item in ratings}

    def _get_comments_dict(self, blog_ids):
        """Get comment counts for blogs."""
        comments = Review.objects.filter(blog_id__in=blog_ids).values('blog_id').annotate(
            comments_count=Count('comments')
        )

        return {item['blog_id']: item['comments_count'] for item in comments}

    def _prepare_blog_data(self, blog, ratings_dict, comments_dict):
        """Prepare data structure for a single blog."""
        try:
            blog_tags = blog.tags if blog.tags and isinstance(blog.tags, list) else []

            location_code = blog.author.profile.location if hasattr(blog.author, 'profile') else None
            location_info = get_location_info(location_code)

            rating_info = ratings_dict.get(blog.id, {'avg_rating': 0, 'review_count': 0})
            comments_count = comments_dict.get(blog.id, 0)

            return {
                'blog': blog,
                'location_code': location_code,
                'location_info': location_info,
                'blog_tags': blog_tags,
                'avg_rating': rating_info['avg_rating'],
                'review_count': rating_info['review_count'],
                'comments_count': comments_count
            }
        except Exception:
            return {
                'blog': blog,
                'location_code': None,
                'location_info': get_location_info(None),
                'blog_tags': [],
                'avg_rating': 0,
                'review_count': 0,
                'comments_count': 0
            }


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogapp/blog_detail.html'
    context_object_name = 'blog'

    def get_queryset(self):
        return super().get_queryset().select_related('author').prefetch_related('reviews__comments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        blog_tags = []

        if blog.tags:
            blog_tags = blog.tags if isinstance(blog.tags, list) else []

        reviews = blog.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
            avg_rating = round(avg_rating, 1) if avg_rating else 0
            review_count = reviews.count()

            comments_data = reviews.aggregate(
                comments_count=Count('comments')
            )
            comments_count = comments_data['comments_count']
        else:
            avg_rating = 0
            review_count = 0
            comments_count = 0

        context['blog_tags'] = blog_tags
        context['location_info'] = get_location_info(
            blog.author.profile.location if hasattr(blog.author, 'profile') else None
        )
        context['avg_rating'] = avg_rating
        context['review_count'] = review_count
        context['comments_count'] = comments_count
        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'content', 'image', 'tags']
    template_name = 'blogapp/blog_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, '¡El blog ha sido creado exitosamente!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ['title', 'content', 'image', 'tags']
    template_name = 'blogapp/blog_form.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            messages.error(request, "No tienes permiso para editar este blog.")
            return redirect('blogapp:blog_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Eliminar imagen
        if self.request.POST.get('remove_image') == "1":
            form.instance.remove_image()
        form.instance.last_updated = datetime.now()
        messages.success(self.request, '¡El blog ha sido actualizado exitosamente!')
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
            messages.error(request, "No tienes permiso para eliminar este blog.")
            return redirect('blogapp:blog_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        blog = self.get_object()
        # Delete associated image file if exists
        if blog.image:
            blog.image.delete(save=False)
        messages.success(request, '¡El blog ha sido eliminado exitosamente!')
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
        blog = Blog.objects.get(pk=self.kwargs['pk'])
        # Verificar si el usuario ya dejó una reseña para este blog
        if Review.objects.filter(blog=blog, reviewer=self.request.user).exists():
            messages.error(self.request, 'Ya has dejado una reseña para este blog.')
            return redirect('blogapp:blog_detail', pk=blog.pk)

        form.instance.reviewer = self.request.user
        form.instance.blog = blog
        messages.success(self.request, '¡Tu reseña ha sido publicada exitosamente!')
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
        messages.success(self.request, '¡Tu comentario ha sido publicado exitosamente!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['blog_pk']})


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Usuario'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Contraseña'
        })
    )


class LogoutView(RedirectView):
    url = reverse_lazy('blogapp:blog_list')
    
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return super().get(request, *args, **kwargs)


class SignUpView(FormView):
    template_name = 'blogapp/register_modal.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('blogapp:login_modal')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, '¡Tu cuenta ha sido creada exitosamente!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores a continuación.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['errors'] = self.get_form().errors.get_json_data() if self.request.method == 'POST' else None
        return context
        
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blogapp:blog_list')
        return super().dispatch(request, *args, **kwargs)

        # modal login view
class LoginView(FormView):
    template_name = 'blogapp/login_modal.html'
    form_class = LoginForm
    success_url = reverse_lazy('blogapp:blog_list')

    def form_valid(self, form):
        username = form.cleaned_data.get("username", "")
        password = form.cleaned_data.get("password", "")
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, '¡Inicio de sesión exitoso!')
            next_url = self.request.GET.get('next', self.get_success_url())
            return redirect(next_url)

        messages.error(self.request, 'Usuario o contraseña inválidos.')
        return self.form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blogapp:blog_list')
        return super().dispatch(request, *args, **kwargs)
    
 # modal register view
class RegisterView(FormView):
    """
    Modal registration view with improved validation
    """
    template_name = 'blogapp/register_modal.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blogapp:login_modal')

    def form_valid(self, form):
        User = form.save()
        messages.success(
            self.request,
            '¡Registro exitoso! Por favor inicia sesión con tus nuevas credenciales.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Debes cerrar sesión para registrar una nueva cuenta.')
            return redirect('blogapp:blog_list')
        return super().dispatch(request, *args, **kwargs)

@login_required
def add_comment(request, blog_pk, review_pk):
    """
    Vista para agregar un comentario a una reseña específica de un blog.
    """
    review = get_object_or_404(Review, pk=review_pk, blog__pk=blog_pk)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()  # Obtener y limpiar el contenido del comentario
        if content:
            # Crear el comentario si el contenido no está vacío
            Comment.objects.create(
                review=review,
                commenter=request.user,
                content=content
            )
            messages.success(request, '¡Tu comentario ha sido publicado exitosamente!')
        else:
            # Mostrar un mensaje de error si el contenido está vacío
            messages.error(request, 'El comentario no puede estar vacío.')

    # Redirigir de vuelta al detalle del blog
    return redirect('blogapp:blog_detail', pk=blog_pk)
