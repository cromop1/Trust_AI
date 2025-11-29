from django.contrib import admin

from .models import ChatSession, Message, StyleTemplate


@admin.register(StyleTemplate)
class StyleTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "description", "system_prompt")
    prepopulated_fields = {"name": ("title",)}


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "content", "tokens_used", "created_at")
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "model_choice", "style_template", "updated_at")
    list_filter = ("model_choice", "style_template")
    search_fields = ("title", "user__email", "user__display_name")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "created_at", "short_content", "tokens_used")
    list_filter = ("role",)
    search_fields = ("content", "session__title", "session__user__email")

    def short_content(self, obj):
        return obj.content[:60] + ("…" if len(obj.content) > 60 else "")

    short_content.short_description = "Contenido"
