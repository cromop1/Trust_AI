from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom manager that uses the email address as the username field."""

    use_in_migrations = True

    def create_user(self, email: str | None, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            raise ValueError("La contraseña es obligatoria.")
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str | None, password: str | None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with profile fields and email-based authentication."""

    username = models.CharField(_("username"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    display_name = models.CharField(_("display name"), max_length=150, blank=True)
    bio = models.TextField(_("biografía"), blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deepseek_api_key = models.CharField(
        _("DeepSeek API key"),
        max_length=255,
        blank=True,
        help_text=_("Clave privada usada para conectar tus chats directamente con DeepSeek."),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = _("usuario")
        verbose_name_plural = _("usuarios")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.display_name or self.email

    def save(self, *args, **kwargs):
        if not self.display_name:
            base_name = self.username or (self.email.split("@")[0] if self.email else "")
            self.display_name = base_name
        super().save(*args, **kwargs)

    @property
    def profile_initials(self) -> str:
        if self.display_name:
            parts = self.display_name.split()
            return "".join(part[0].upper() for part in parts[:2])
        if self.email:
            return self.email[0].upper()
        return "?"

    @property
    def active_subscription(self):
        now = timezone.now()
        # Limpia suscripciones expiradas de forma perezosa.
        self.subscriptions.filter(is_active=True, expires_at__lte=now).update(is_active=False)
        return (
            self.subscriptions.filter(is_active=True, expires_at__gt=now)
            .order_by("-expires_at")
            .first()
        )

    @property
    def has_active_subscription(self) -> bool:
        return self.active_subscription is not None


class SubscriptionCode(models.Model):
    code = models.CharField(max_length=64, unique=True)
    plan_name = models.CharField(max_length=150)
    duration_days = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(blank=True, null=True)
    activated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="redeemed_subscription_codes",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "código de suscripción"
        verbose_name_plural = "códigos de suscripción"

    def __str__(self) -> str:
        return f"{self.plan_name} · {self.code}"

    @property
    def is_redeemed(self) -> bool:
        return self.activated_at is not None

    def mark_redeemed(self, user: User) -> None:
        self.is_active = False
        self.activated_by = user
        self.activated_at = timezone.now()
        self.save(update_fields=["is_active", "activated_by", "activated_at"])

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)


class UserSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="subscriptions",
        on_delete=models.CASCADE,
    )
    plan_name = models.CharField(max_length=150)
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    code = models.ForeignKey(
        SubscriptionCode,
        related_name="activations",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-expires_at",)
        verbose_name = "suscripción de usuario"
        verbose_name_plural = "suscripciones de usuarios"

    def __str__(self) -> str:
        return f"{self.user.display_name or self.user.email} · {self.plan_name}"

    @property
    def is_valid(self) -> bool:
        return self.expires_at > timezone.now()

    @property
    def days_remaining(self) -> int:
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)

    def save(self, *args, **kwargs):
        self.is_active = self.expires_at > timezone.now()
        super().save(*args, **kwargs)
