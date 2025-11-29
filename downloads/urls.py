from django.urls import path

from .views import ResourceDetailView, ResourceListView

app_name = "downloads"

urlpatterns = [
    path("", ResourceListView.as_view(), name="list"),
    path("<int:pk>/", ResourceDetailView.as_view(), name="detail"),
]
