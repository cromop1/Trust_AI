from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import SubscriptionCode, User, UserSubscription


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("email", "display_name", "is_staff", "is_active", "last_login")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("email",)
    search_fields = ("email", "display_name", "username")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {"fields": ("display_name", "username", "bio", "avatar")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("last_login", "date_joined")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "display_name", "password1", "password2"),
            },
        ),
    )


@admin.register(SubscriptionCode)
class SubscriptionCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "plan_name", "duration_days", "is_active", "activated_by", "activated_at", "created_at")
    list_filter = ("is_active", "plan_name", "duration_days")
    search_fields = ("code", "plan_name")
    readonly_fields = ("activated_at", "activated_by", "created_at")
    ordering = ("-created_at",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan_name", "started_at", "expires_at", "is_active")
    list_filter = ("plan_name", "is_active")
    search_fields = ("user__email", "user__display_name", "plan_name")
    readonly_fields = ("created_at",)
