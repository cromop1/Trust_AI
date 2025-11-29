from __future__ import annotations

from django import forms

from .models import ChatSession, Message, StyleTemplate


class ChatSessionCreateForm(forms.ModelForm):
    class Meta:
        model = ChatSession
        fields = ("style_template", "model_choice", "title")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Ponle un nombre a tu conversación"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        favorites_only = kwargs.pop("favorites_only", False)
        super().__init__(*args, **kwargs)
        queryset = StyleTemplate.objects.filter(is_active=True)
        if favorites_only and user is not None:
            queryset = queryset.filter(favorite_users=user)
        self.fields["style_template"].queryset = queryset
        self.fields["style_template"].empty_label = None
        self.fields["model_choice"].label = "Motor de TrustAI"
        self.fields["style_template"].label = "Plantilla de estilo"
        self.fields["title"].label = "Título del chat"
        if user:
            self.initial.setdefault("title", f"Nuevo chat de {user.display_name or user.email}")


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Escribe tu mensaje para TrustAI…",
                }
            ),
        }
        labels = {
            "content": "",
        }

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError("El mensaje no puede estar vacío.")
        return content
