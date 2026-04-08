from datetime import datetime
import secrets
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileUpdateForm, PasswordUpdateForm, EmailUpdateForm, ProfileDeletionForm
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, RedirectView
from django.urls import reverse_lazy, reverse
from .models import Blog, Review, Comment, UserProfile
from django.contrib.messages import get_messages
from social_core.exceptions import AuthCanceled, AuthForbidden
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django import forms
from django.db.models import Avg, Count, Q
from django.db.utils import OperationalError, ProgrammingError
from django.contrib.auth.forms import UserCreationForm
from random import choice
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.http import HttpResponse


logger = logging.getLogger(__name__)


def get_location_info(location_code):
    LOCATION_MAP = {
        'BOC': {'flag_url': 'Bocas_del_Toro', 'name': 'Bocas del Toro', 'color': 'lime'},
        'CHI': {'flag_url': 'Chiriqui', 'name': 'República Federal de Chiriquí', 'color': 'green'},
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

    def _get_viewed_user(self):
        username = (self.kwargs.get('username') or '').strip()
        if not username:
            return None
        user = get_user_model().objects.filter(username__iexact=username).first()
        if user:
            return user

        request_user = getattr(self.request, 'user', None)
        if (
            request_user
            and request_user.is_authenticated
            and (request_user.username or '').strip().lower() == username.lower()
        ):
            return request_user

        return None

    def get_object(self, queryset=None):
        user = self._get_viewed_user()
        if not user:
            return None

        try:
            return UserProfile.objects.filter(user=user).first()
        except (OperationalError, ProgrammingError):
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewed_user = self._get_viewed_user()
        if not viewed_user:
            context['profile_user'] = None
            context['blogs'] = []
            context['profile'] = None
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

        context['profile_user'] = viewed_user
        profile = self.get_object()
        context['profile'] = profile

        # Profile info
        context['interests_list'] = profile.interests if profile and profile.interests else []
        context['location_info'] = get_location_info(profile.location if profile else None)

        try:
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
        except (OperationalError, ProgrammingError):
            context['blogs'] = []
            context['blogs_count'] = 0
            context['reviews_list'] = []
            context['reviews_count'] = 0
            context['reviewed_blogs'] = []
            context['average_rating'] = 0
            context['average_review_rating'] = 0
            context['comments_list'] = []
            context['comments_count'] = 0
            context['commented_blogs'] = []
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
    form_class = ProfileUpdateForm
    template_name = 'blogapp/profile_form.html'
    success_url = None

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            # Create a profile if it doesn't exist
            return UserProfile.objects.create(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('username') != request.user.username:
            return redirect('blogapp:profile_settings', username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Update UserProfile fields
        profile = form.save(commit=False)
        profile.save()

        # Update User fields
        user = self.request.user
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.username = form.cleaned_data.get('username', '')
        user.save()

        messages.success(self.request, '¡Tu perfil ha sido actualizado exitosamente!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:profile', kwargs={'username': self.request.user.username})

class ProfileSettingsView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'blogapp/profile_settings.html'
    context_object_name = 'profile'

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('username') != request.user.username:
            return redirect('blogapp:profile_settings', username=request.user.username)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            # Create a profile if it doesn't exist
            return UserProfile.objects.create(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        password_token = secrets.token_urlsafe(24)
        email_token = secrets.token_urlsafe(24)
        delete_token = secrets.token_urlsafe(24)

        self.request.session['profile_settings_password_access_token'] = password_token
        self.request.session['profile_settings_email_access_token'] = email_token
        self.request.session['profile_settings_delete_access_token'] = delete_token

        context['password_change_access_url'] = (
            reverse('blogapp:password_change', kwargs={'username': self.request.user.username})
            + f'?access={password_token}'
        )
        context['email_change_access_url'] = (
            reverse('blogapp:email_change', kwargs={'username': self.request.user.username})
            + f'?access={email_token}'
        )
        context['delete_profile_access_url'] = (
            reverse('blogapp:delete_profile', kwargs={'username': self.request.user.username})
            + f'?access={delete_token}'
        )

        return context


class ProfileSettingsAccessRequiredMixin:
    access_token_session_key = ''
    active_form_session_key = ''

    def _settings_redirect(self):
        return redirect('blogapp:profile_settings', username=self.request.user.username)

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('username') != request.user.username:
            return self._settings_redirect()

        if request.method == 'GET':
            access_token = request.GET.get('access', '')
            expected_token = request.session.get(self.access_token_session_key, '')

            if not access_token or access_token != expected_token:
                return self._settings_redirect()

            request.session.pop(self.access_token_session_key, None)
            request.session[self.active_form_session_key] = True

        elif request.method == 'POST':
            if not request.session.get(self.active_form_session_key, False):
                return self._settings_redirect()

        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


class PasswordUpdateView(LoginRequiredMixin, ProfileSettingsAccessRequiredMixin, FormView):
    form_class = PasswordUpdateForm
    template_name = 'blogapp/profile_update_password.html'
    success_url = reverse_lazy('blogapp:profile')
    access_token_session_key = 'profile_settings_password_access_token'
    active_form_session_key = 'profile_settings_password_access_active'

    def form_valid(self, form):
        user = self.request.user
        new_password = form.cleaned_data.get('new_password')
        user.set_password(new_password)
        user.save()
        messages.success(self.request, '¡Tu contraseña ha sido actualizada exitosamente!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:profile', kwargs={'username': self.request.user.username})

class EmailUpdateView(LoginRequiredMixin, ProfileSettingsAccessRequiredMixin, FormView):
    form_class = EmailUpdateForm
    template_name = 'blogapp/profile_update_email.html'
    success_url = reverse_lazy('blogapp:profile')
    access_token_session_key = 'profile_settings_email_access_token'
    active_form_session_key = 'profile_settings_email_access_active'

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data.get('new_email')
        user.email = new_email
        user.save()
        messages.success(self.request, '¡Tu correo electrónico ha sido actualizado exitosamente!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:profile', kwargs={'username': self.request.user.username})

class ProfileDeleteView(LoginRequiredMixin, ProfileSettingsAccessRequiredMixin, FormView):
    form_class = ProfileDeletionForm
    template_name = 'blogapp/profile_confirm_delete.html'
    success_url = reverse_lazy('blogapp:blog_list')
    access_token_session_key = 'profile_settings_delete_access_token'
    active_form_session_key = 'profile_settings_delete_access_active'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user

        try:
            profile = user.profile
            # Delete profile photo if exists
            if profile and profile.profile_photo:
                profile.profile_photo.delete(save=False)
        except UserProfile.DoesNotExist:
            pass

        # Store session key before user deletion
        session_key = self.request.session.session_key

        # Delete the user (this will also delete the profile via cascade)
        user.delete()

        # Clear the session
        if session_key:
            Session.objects.filter(session_key=session_key).delete()

        messages.success(self.request, '¡Tu perfil ha sido eliminado exitosamente!')
        return redirect(self.success_url)

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
        try:
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
                    review_count=Count('reviews'),
                    avg_rating=Avg('reviews__rating')
                ).order_by('-review_count', '-avg_rating', '-created_at')
            elif sort == 'random':
                blog_ids = Blog.objects.values_list('id', flat=True)
                if blog_ids:
                    random_id = choice(list(blog_ids))
                    self.random_blog_id = random_id
                    queryset = queryset.filter(id=random_id)
                else:
                    queryset = queryset.none()
            else:
                queryset = queryset.order_by('-created_at')

            return self._apply_filters(queryset)
        except (OperationalError, ProgrammingError):
            return Blog.objects.none()

    def _apply_filters(self, queryset):
        """Apply all filters from request parameters to the queryset."""
        search_query = self.request.GET.get('search', '').strip()
        tag = self.request.GET.get('tag', '').strip()
        author = self.request.GET.get('author', '').strip()
        province = (self.request.GET.get('province') or self.request.GET.get('location', '')).strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()

        # Construir el filtro Q para OR global
        q_objects = Q()
        if search_query:
            q_objects |= Q(title__icontains=search_query)
            q_objects |= Q(content__icontains=search_query)
            q_objects |= Q(tags__icontains=search_query)
            q_objects |= Q(author__username__icontains=search_query)
            q_objects |= Q(author__profile__location__icontains=search_query)
        if tag:
            q_objects |= Q(tags__icontains=tag)
        if author:
            q_objects |= Q(author__username__icontains=author)
        if province:
            q_objects |= Q(author__profile__location__icontains=province)
        if date_from:
            q_objects |= Q(created_at__gte=date_from)
        if date_to:
            q_objects |= Q(created_at__lte=date_to)

        if q_objects:
            queryset = queryset.filter(q_objects).distinct()

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
        
        user = self.request.user
        if user.is_authenticated and user != blog.author:
            has_reviewed = blog.reviews.filter(reviewer=user).exists()
        else:
            has_reviewed = False
        context['can_add_review'] = user.is_authenticated and user != blog.author and not has_reviewed
        return context


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ['title', 'content', 'image', 'tags']
    template_name = 'blogapp/blog_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        try:
            response = super().form_valid(form)
        except Exception as exc:
            logger.exception('Fallo al subir imagen en BlogCreateView: %s', exc)
            # Si falla la subida (Cloudinary o filesystem), guardar el blog sin imagen para evitar 500.
            if form.cleaned_data.get('image'):
                form.instance.image = None
                self.object = form.save()
                messages.warning(
                    self.request,
                    'El blog se creó, pero la imagen no pudo guardarse en este momento.'
                )
                messages.success(self.request, '¡El blog ha sido creado exitosamente!')
                return redirect(self.get_success_url())
            raise

        messages.success(self.request, '¡El blog ha sido creado exitosamente!')
        return response

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
        try:
            response = super().form_valid(form)
        except Exception as exc:
            logger.exception('Fallo al subir imagen en BlogUpdateView: %s', exc)
            if form.cleaned_data.get('image'):
                original_blog = self.get_object()
                form.instance.image = original_blog.image
                self.object = form.save()
                messages.warning(
                    self.request,
                    'El blog se actualizó, pero la nueva imagen no pudo guardarse en este momento.'
                )
                messages.success(self.request, '¡El blog ha sido actualizado exitosamente!')
                return redirect(self.get_success_url())
            raise

        messages.success(self.request, '¡El blog ha sido actualizado exitosamente!')
        return response

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
        form.save()
        messages.success(self.request, '¡Registro exitoso! Por favor inicia sesión con tus nuevas credenciales.')
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('', status=204)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, {'form': form, 'messages': messages.get_messages(self.request)}, self.request)
            return HttpResponse(html)
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
