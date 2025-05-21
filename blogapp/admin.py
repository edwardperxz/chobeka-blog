from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.sites.models import Site
from social_django.models import Association, Nonce, UserSocialAuth
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from .models import BlogStats, Blog, Review, Comment
from .admin_stats import BlogStatsAdmin

# Custom admin site
class CustomAdminSite(admin.AdminSite):
    site_header = "Blog de Memes Admin"
    site_title = "Panel de Administración"
    index_title = "Bienvenido al Dashboard"

admin_site = CustomAdminSite(name='admin')

# Registra modelos predeterminados y de terceros
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Site)  # Sites

admin_site.register(EmailAddress)

admin_site.register(SocialAccount)
admin_site.register(SocialApp)
admin_site.register(SocialToken)

# Python Social Auth
admin_site.register(Association)
admin_site.register(Nonce)
admin_site.register(UserSocialAuth)

# Registrar el modelo virtual para las estadísticas

@admin.register(Blog, site=admin_site)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    list_filter = ("author", "created_at")
    search_fields = ("title", "content")
    ordering = ("-created_at",)
    list_per_page = 10

@admin.register(Review, site=admin_site)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("blog", "reviewer", "rating", "created_at")
    list_filter = ("blog", "reviewer", "rating", "created_at")
    search_fields = ("blog__title", "reviewer__username", "comment")
    ordering = ("-created_at",)
    list_per_page = 10

@admin.register(Comment, site=admin_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("review", "commenter", "content", "created_at")
    list_filter = ("review", "commenter", "created_at")
    search_fields = ("review__blog__title", "commenter__username", "content")
    ordering = ("-created_at",)
    list_per_page = 10

admin_site.register(BlogStats, BlogStatsAdmin)