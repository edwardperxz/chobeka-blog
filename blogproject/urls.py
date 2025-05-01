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
<<<<<<< HEAD
from blogapp.views import social_auth_error

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blogapp.urls')),  
    path('accounts/', include('allauth.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('social-auth-error/', social_auth_error, name='social_auth_error'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blogapp.urls')),  # Conecta las URLs de blogapp
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
>>>>>>> b61a8fc60e9d38d950e69fb10e0f3390a729539a
