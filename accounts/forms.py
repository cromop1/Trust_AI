from __future__ import annotations

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(label="Contraseña", strip=False, widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Credenciales inválidas. Verifica tu correo y contraseña.",
        "inactive": "Esta cuenta está desactivada.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages["inactive"], code="inactive")

        return cleaned_data

    def get_user(self):
        return self.user_cache


class UserRegistrationForm(UserCreationForm):
    display_name = forms.CharField(
        label="Nombre a mostrar",
        max_length=150,
        help_text="Será visible en la plataforma.",
    )
    bio = forms.CharField(
        label="Biografía",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    avatar = forms.ImageField(label="Avatar", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "display_name", "bio", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email")
        display_name = self.cleaned_data.get("display_name")
        base_username = (display_name or (email.split("@")[0] if email else "") or "usuario").replace(" ", "").lower()
        unique_username = base_username
        counter = 1
        while User.objects.filter(username=unique_username).exists():
            counter += 1
            unique_username = f"{base_username}{counter}"
        user.username = unique_username
        user.display_name = display_name or email
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserProfileForm(forms.ModelForm):
    deepseek_api_key = forms.CharField(
        label="API key de DeepSeek",
        required=False,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                "placeholder": "sk-xxx",
                "autocomplete": "off",
            },
        ),
        help_text="Clave obligatoria para enviar mensajes. Solo se usa en tus conversaciones.",
    )

    class Meta:
        model = User
        fields = ("display_name", "bio", "avatar", "deepseek_api_key")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "avatar": forms.ClearableFileInput(attrs={"accept": "image/*", "hidden": "hidden"}),
        }

    def clean_deepseek_api_key(self):
        value = self.cleaned_data.get("deepseek_api_key", "")
        return value.strip()
