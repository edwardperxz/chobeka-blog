from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Correo electrónico'
        })
    )

    username = forms.CharField(
        label='',  # Elimina el label del campo username
        widget=forms.TextInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Nombre de usuario'
        })
    )

    password1 = forms.CharField(
        required=True,
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        required=True,
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirmar contraseña'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
