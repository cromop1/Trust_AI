from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class StyleTemplate(models.Model):
    name = models.SlugField(unique=True, max_length=100)
    title = models.CharField(max_length=150)
    description = models.TextField()
    system_prompt = models.TextField()
    is_active = models.BooleanField(default=True)
    favorite_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="favorite_style_templates",
        blank=True,
    )
    reactions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="StyleTemplateReaction",
        related_name="style_template_reactions",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title",)
        verbose_name = "plantilla de estilo"
        verbose_name_plural = "plantillas de estilo"

    def __str__(self) -> str:
        return self.title


class ChatSession(models.Model):
    class ModelChoices(models.TextChoices):
        CHAT = "trustai-chat", "TrustAI Chat"
        CODER = "trustai-coder", "TrustAI Coder"
        REASONER = "trustai-reasoner", "TrustAI Reasoner"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField(max_length=200)
    model_choice = models.CharField(max_length=32, choices=ModelChoices.choices, default=ModelChoices.CHAT)
    style_template = models.ForeignKey(StyleTemplate, on_delete=models.PROTECT, related_name="chat_sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "sesión de chat"
        verbose_name_plural = "sesiones de chat"

    def __str__(self) -> str:
        return f"{self.title} · {self.get_model_choice_display()}"

    def refresh_activity(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])

    @property
    def total_messages(self) -> int:
        return self.messages.count()

    @property
    def total_tokens(self) -> int:
        return self.messages.aggregate(total=models.Sum("tokens_used")).get("total") or 0


class Message(models.Model):
    class Roles(models.TextChoices):
        USER = "user", "Usuario"
        ASSISTANT = "assistant", "Asistente"
        SYSTEM = "system", "Sistema"

    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Roles.choices)
    content = models.TextField()
    tokens_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "mensaje"
        verbose_name_plural = "mensajes"

    def __str__(self) -> str:
        return f"{self.get_role_display()} · {self.created_at:%Y-%m-%d %H:%M}"


class StyleTemplateReaction(models.Model):
    class Values(models.IntegerChoices):
        LIKE = 1, "Me gusta"
        DISLIKE = -1, "No me gusta"

    style = models.ForeignKey(StyleTemplate, related_name="style_reactions", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_style_reactions", on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=Values.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("style", "user")
        verbose_name = "reacción de estilo"
        verbose_name_plural = "reacciones de estilo"

    def __str__(self) -> str:
        return f"{self.user} → {self.style} ({self.get_value_display()})"
