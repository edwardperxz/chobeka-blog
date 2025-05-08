from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_('Correo electrónico'),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Correo electrónico'
        })
    )

    username = forms.CharField(
        label=_('Nombre de usuario'),
        widget=forms.TextInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Nombre de usuario'
        })
    )

    password1 = forms.CharField(
        required=True,
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        required=True,
        label=_('Confirmar contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirmar contraseña'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages = {
            'password_mismatch': _('Las contraseñas no coinciden.'),
        }
        
        # Personaliza los textos de ayuda
        self.fields['password1'].help_text = _(
            'Tu contraseña debe contener al menos 8 caracteres, no puede ser '
            'completamente numérica y no puede ser demasiado común.'
        )
        
        # Personaliza las etiquetas
        self.fields['username'].label = _('Nombre de usuario')
        self.fields['password1'].label = _('Contraseña')
        self.fields['password2'].label = _('Confirmar contraseña')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        # Solo validar coincidencia, omitir otras validaciones
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                "Las contraseñas no coinciden.",
                code='password_mismatch',
            )
        return password2