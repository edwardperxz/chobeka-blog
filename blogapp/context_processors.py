import random
import os
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError
from .models import Blog

def recommended_blogs(request):
    """
    Devuelve una lista de blogs aleatorios para el sidebar derecho.
    """
    try:
        blogs = list(Blog.objects.select_related('author').prefetch_related('reviews').all())
        random.shuffle(blogs)
    except (OperationalError, ProgrammingError):
        blogs = []
    return {
        'recommended_blogs': blogs[:12]
    }

def env_flags(request):
    return {
        'debug': settings.DEBUG,
        'pythonanywhere': 'PYTHONANYWHERE_DOMAIN' in os.environ,
        'enable_social_auth': getattr(settings, 'ENABLE_SOCIAL_AUTH', False),
    }