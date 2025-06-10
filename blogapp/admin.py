from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.sites.models import Site
from django.utils.html import format_html
from social_django.models import Association, Nonce, UserSocialAuth
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from .models import BlogStats, Blog, Review, Comment
from .admin_stats import BlogStatsAdmin
from .admin_tools import get_last_restart, COOLDOWN_SECONDS
import time

# Custom admin site
class CustomAdminSite(admin.AdminSite):
    site_header = "Blog de Memes Admin"
    site_title = "Panel de Administración"
    index_title = "Bienvenido al Dashboard"
    index_template = "admin/index.html" 

    def each_context(self, request):
        context = super().each_context(request)
        now = time.time()
        last_restart = get_last_restart()
        remaining = max(0, int(COOLDOWN_SECONDS - (now - last_restart)))
        context['restart_cooldown_remaining'] = remaining
        return context

admin_site = CustomAdminSite(name='admin')

# Registra modelos predeterminados y de terceros
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Site)

# Social authentication models
class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'verified', 'primary')
    search_fields = ('email', 'user__username')
    list_filter = ('verified', 'primary')

admin_site.register(EmailAddress, EmailAddressAdmin)

class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'uid')
    search_fields = ('user__username', 'provider')
    list_filter = ('provider',)

admin_site.register(SocialAccount, SocialAccountAdmin)
admin_site.register(SocialApp)
admin_site.register(SocialToken)

# Python Social Auth
admin_site.register(Association)
admin_site.register(Nonce)
admin_site.register(UserSocialAuth)

@admin.register(Blog, site=admin_site)
class BlogAdmin(admin.ModelAdmin):
    def blog_actions(self, obj):
        view_url = f"/blog/{obj.id}/"
        edit_url = f"/admin/blogapp/blog/{obj.id}/change/"
        delete_url = f"/admin/blogapp/blog/{obj.id}/delete/"

        return format_html(
            '<a href="{}" class="button" style="background-color:#4CAF50;color:white;padding:4px 8px;margin:2px;border-radius:4px;text-decoration:none;" target="_blank">View</a> '
            '<a href="{}" class="button" style="background-color:#2196F3;color:white;padding:4px 8px;margin:2px;border-radius:4px;text-decoration:none;">Edit</a> '
            '<a href="{}" class="button" style="background-color:#f44336;color:white;padding:4px 8px;margin:2px;border-radius:4px;text-decoration:none;">Delete</a>',
            view_url, edit_url, delete_url
        )

    list_display = ("title", "author", "created_at", "blog_actions")
    list_filter = ("author", "created_at")
    search_fields = ("title", "content")
    ordering = ("-created_at",)
    list_per_page = 15
    date_hierarchy = 'created_at'

    blog_actions.short_description = 'Actions'

@admin.register(Review, site=admin_site)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("blog", "reviewer", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("blog__title", "reviewer__username", "comment")
    ordering = ("-created_at",)
    list_per_page = 15
    date_hierarchy = 'created_at'
    raw_id_fields = ('blog', 'reviewer')

@admin.register(Comment, site=admin_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("review", "commenter", "short_content", "created_at")
    list_filter = ("created_at",)
    search_fields = ("review__blog__title", "commenter__username", "content")
    ordering = ("-created_at",)
    list_per_page = 15
    date_hierarchy = 'created_at'
    raw_id_fields = ('review', 'commenter')

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"

admin_site.register(BlogStats, BlogStatsAdmin)