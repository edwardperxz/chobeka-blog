from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Comment, UserProfile, User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_('Correo electrónico'),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Correo electrónico'
        }),
        error_messages={
            'required': _('Este campo es obligatorio.'),
            'invalid': _('Introduce una dirección de correo válida.'),
        }
    )

    username = forms.CharField(
        label=_('Nombre de usuario'),
        widget=forms.TextInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Nombre de usuario'
        }),
        error_messages={
            'required': _('Este campo es obligatorio.'),
            'unique': _('Este nombre de usuario ya está en uso.'),
        }
    )

    password1 = forms.CharField(
        required=True,
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Contraseña'
        }),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
    )
    password2 = forms.CharField(
        required=True,
        label=_('Confirmar contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirmar contraseña'
        }),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
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
                _("Las contraseñas no coinciden."),
                code='password_mismatch',
            )
        return password2

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or content.strip() == "":
            raise forms.ValidationError("El comentario no puede estar vacío.")
        return content

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    username = forms.CharField(max_length=20, required=True)

    class Meta:
        model = UserProfile
        fields = ['profile_photo', 'bio', 'location', 'birth_date', 'interests']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['username'].initial = user.username


class PasswordUpdateForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Contraseña actual'
        }),
        required=True,
        label=_('Contraseña actual'),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Nueva contraseña'
        }),
        required=True,
        label=_('Nueva contraseña'),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        required=True,
        label=_('Confirmar nueva contraseña'),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError(_("La contraseña actual es incorrecta"))
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError(_("Las nuevas contraseñas no coinciden"))
            if len(new_password1) < 8:
                raise ValidationError(_("La contraseña debe tener al menos 8 caracteres"))
        return cleaned_data

    def save(self):
        new_password = self.cleaned_data.get('new_password1')
        self.user.set_password(new_password)
        self.user.save()
        return self.user


class EmailUpdateForm(forms.Form):
    new_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Nuevo correo electrónico'
        }),
        required=True,
        label=_('Nuevo correo electrónico'),
        error_messages={
            'required': _('Este campo es obligatorio.'),
            'invalid': _('Introduce una dirección de correo válida.'),
        }
    )
    confirm_new_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirmar nuevo correo electrónico'
        }),
        required=True,
        label=_('Confirmar nuevo correo electrónico'),
        error_messages={
            'required': _('Este campo es obligatorio.'),
            'invalid': _('Introduce una dirección de correo válida.'),
        }
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('new_email')
        confirm_new_email = cleaned_data.get('confirm_new_email')

        if new_email and confirm_new_email:
            if new_email != confirm_new_email:
                raise ValidationError(_("Los correos electrónicos no coinciden"))

            # Check if email already exists
            if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
                raise ValidationError(_("Este correo electrónico ya está en uso"))

        return cleaned_data

    def save(self):
        new_email = self.cleaned_data.get('new_email')
        self.user.email = new_email
        self.user.save()
        return self.user


class ProfileDeletionForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Nombre de usuario'
        }),
        required=True,
        label=_('Nombre de usuario'),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg w-full border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Contraseña'
        }),
        required=True,
        label=_('Contraseña'),
        error_messages={
            'required': _('Este campo es obligatorio.'),
        }
    )
    confirmation = forms.BooleanField(
        required=True,
        label=_('Confirmo que deseo eliminar mi cuenta permanentemente'),
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500'
        }),
        error_messages={
            'required': _('Debes confirmar que deseas eliminar tu cuenta.'),
        }
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.user.username != username:
            raise ValidationError(_("El nombre de usuario no coincide con tu cuenta"))
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError(_("La contraseña es incorrecta"))
        return password