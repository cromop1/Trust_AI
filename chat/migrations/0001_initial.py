from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StyleTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.SlugField(max_length=100, unique=True)),
                ("title", models.CharField(max_length=150)),
                ("description", models.TextField()),
                ("system_prompt", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("title",),
                "verbose_name": "plantilla de estilo",
                "verbose_name_plural": "plantillas de estilo",
            },
        ),
        migrations.CreateModel(
            name="ChatSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                (
                    "model_choice",
                    models.CharField(
                        choices=[
                            ("deepseek-chat", "DeepSeek Chat"),
                            ("deepseek-coder", "DeepSeek Coder"),
                            ("deepseek-reasoner", "DeepSeek Reasoner"),
                        ],
                        default="deepseek-chat",
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "style_template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="chat_sessions",
                        to="chat.styletemplate",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_sessions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-updated_at",),
                "verbose_name": "sesión de chat",
                "verbose_name_plural": "sesiones de chat",
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "role",
                    models.CharField(
                        choices=[("user", "Usuario"), ("assistant", "Asistente"), ("system", "Sistema")],
                        max_length=20,
                    ),
                ),
                ("content", models.TextField()),
                ("tokens_used", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="chat.chatsession",
                    ),
                ),
            ],
            options={
                "ordering": ("created_at",),
                "verbose_name": "mensaje",
                "verbose_name_plural": "mensajes",
            },
        ),
    ]
