from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self) -> None:
        # Import signals or other startup logic when needed
        from . import signals  # noqa: F401
        return super().ready()
