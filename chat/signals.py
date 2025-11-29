from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ChatSession, Message


@receiver(post_save, sender=Message)
def update_session_timestamp(sender, instance: Message, created: bool, **kwargs):
    if created:
        ChatSession.objects.filter(pk=instance.session_id).update(updated_at=instance.created_at)
