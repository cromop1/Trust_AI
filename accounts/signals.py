from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_display_name(sender, instance: User, created: bool, **kwargs):
    if created and not instance.display_name:
        instance.display_name = instance.email.split("@")[0] if instance.email else instance.username
        instance.save(update_fields=["display_name"])
