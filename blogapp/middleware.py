from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from social_core.exceptions import AuthCanceled

class SocialAuthExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, AuthCanceled):
            messages.warning(request, "Cancelaste el inicio de sesión con Facebook")
            return redirect(reverse('blogapp:login_modal'))
        return None