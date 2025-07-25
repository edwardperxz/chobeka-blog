import random
import os
from django.conf import settings
from .models import Blog

def recommended_blogs(request):
    """
    Devuelve una lista de blogs aleatorios para el sidebar derecho.
    """
    blogs = list(Blog.objects.select_related('author').prefetch_related('reviews').all())
    random.shuffle(blogs)
    return {
        'recommended_blogs': blogs[:12]
    }

def env_flags(request):
    return {
        'debug': settings.DEBUG,
        'pythonanywhere': 'PYTHONANYWHERE_DOMAIN' in os.environ,
    }