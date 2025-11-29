from __future__ import annotations

from django.conf import settings
from django.db import models


def resource_upload_to(instance: "Resource", filename: str) -> str:
    return f"resources/files/{instance.pk or 'new'}/{filename}"


def resource_image_upload_to(instance: "Resource", filename: str) -> str:
    return f"resources/images/{instance.pk or 'new'}/{filename}"


class Resource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to=resource_image_upload_to, blank=True, null=True)
    file = models.FileField(upload_to=resource_upload_to)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="uploaded_resources",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "recurso descargable"
        verbose_name_plural = "recursos descargables"

    def __str__(self) -> str:
        return self.title

    def extension(self) -> str:
        if not self.file:
            return ""
        return (self.file.name.rsplit(".", 1)[-1]).upper()
