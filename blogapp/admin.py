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
    list_display = ("title", "author")

@admin.register(Review, site=admin_site)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("blog", "reviewer", "rating")

@admin.register(Comment, site=admin_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("review", "commenter")

admin_site.register(BlogStats, BlogStatsAdmin)