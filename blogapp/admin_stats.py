from django.contrib import admin, messages
from django.db.models import Count, Avg
from .models import Blog, Review, Comment, User
from django.urls import path
from django.shortcuts import redirect
from .tasks import export_all_data_to_csv

class BlogStatsAdmin(admin.ModelAdmin):
    change_list_template = "admin/blog_stats.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        total_reviews = Review.objects.count()
        total_comments = Comment.objects.count()
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg']

        top_rated = Blog.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(
            reviews__isnull=False
        ).order_by('-avg_rating')[:10]

        most_commented = Blog.objects.annotate(
            comment_count=Count('reviews__comments', distinct=True)
        ).filter(
            reviews__comments__isnull=False
        ).order_by('-comment_count')[:10]

        # 1. Usuarios con más blogs
        top_bloggers = User.objects.annotate(
            blog_count=Count('blog')
        ).order_by('-blog_count')[:10]

        # 2. Usuarios con blogs mejor puntuados (avg rating >= 4.0)
        top_rated_users = User.objects.annotate(
            avg_rating=Avg('blog__reviews__rating')
        ).filter(
            avg_rating__gte=4.0
        ).order_by('-avg_rating')[:10]

        # 3. Estadísticas por blog
        blog_stats = Blog.objects.annotate(
            review_count=Count('reviews'),
            comment_count=Count('reviews__comments'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-created_at')  # Ordenar por los más recientes

        extra_context.update({
            'total_reviews': total_reviews,
            'total_comments': total_comments,
            'avg_rating': round(avg_rating, 2) if avg_rating else "N/A",
            'top_rated_blogs': top_rated,
            'most_commented_blogs': most_commented,
            'top_bloggers': top_bloggers,
            'top_rated_users': top_rated_users,
            'blog_stats': blog_stats,
        })

        return super().changelist_view(request, extra_context=extra_context)
    
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-csv/', self.admin_site.admin_view(self.export_csv), name='export-csv'),
        ]
        return custom_urls + urls

    def export_csv(self, request):
        # Trigger Celery task
        export_all_data_to_csv.delay()
        self.message_user(request, "Export started! You will be notified when it's ready.", messages.INFO)
        return redirect(reverse('admin:blogapp_blogstatsadmin_changelist'))
