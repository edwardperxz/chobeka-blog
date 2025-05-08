from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from allauth.socialaccount.providers import registry

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self, request, provider_id, error=None, exception=None, **kwargs):

        provider_names = {
            'google': 'Google',
            'facebook': 'Facebook'
        }

        try:
            # Obtener el proveedor
            provider = registry.get_class(provider_id)
            provider_name = provider.name
        except:
            provider_name = provider_names.get(provider_id, provider_id)  # Fallback si no podemos obtener el nombre
            
        # Mapeo de errores comunes
        error = str(error).lower() if error else ''
        if any(err in error for err in ['access_denied', 'cancelled', 'auth_canceled', 'permissions']):
            message = f"Cancelaste el inicio de sesión con {provider_name}"
            messages.warning(request, message) 
        else:
            message = f"Error en autenticación con {provider_name}. Por favor intenta nuevamente."
            messages.error(request, message) 
            
        raise ImmediateHttpResponse(redirect(reverse('blogapp:login')))