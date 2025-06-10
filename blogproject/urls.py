"""
URL configuration for blogproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from blogapp.admin import admin_site 
from blogapp.admin_tools import restart_pythonanywhere_server, get_restart_cooldown

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('blogapp.urls')),  # Conecta las URLs de blogapp
    path('accounts/', include('allauth.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('accounts/google/login/callback/', include('allauth.socialaccount.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('admin-tools/restart-server/', restart_pythonanywhere_server, name='restart_pythonanywhere_server'),
    path('admin/restart_cooldown/', get_restart_cooldown, name='get_restart_cooldown'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
