from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from .models import Resource


class ResourceListView(LoginRequiredMixin, ListView):
    template_name = "downloads/resource_list.html"
    context_object_name = "resources"

    def get_queryset(self):
        return Resource.objects.filter(is_active=True)


class ResourceDetailView(LoginRequiredMixin, DetailView):
    template_name = "downloads/resource_detail.html"
    context_object_name = "resource"
    model = Resource

    def get_queryset(self):
        return Resource.objects.filter(is_active=True)
