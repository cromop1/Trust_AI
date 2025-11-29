from django.urls import path

from .views import (
    DashboardView,
    SendMessageView,
    SessionCreateView,
    SessionDeleteView,
    SessionDetailView,
    SessionListView,
    ToggleFavoriteStyleView,
    ToggleStyleReactionView,
)

app_name = "chat"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("conversaciones/", SessionListView.as_view(), name="session_list"),
    path("conversaciones/nueva/", SessionCreateView.as_view(), name="session_create"),
    path("conversaciones/<int:pk>/", SessionDetailView.as_view(), name="session_detail"),
    path("conversaciones/<int:pk>/enviar/", SendMessageView.as_view(), name="message_send"),
    path("conversaciones/<int:pk>/eliminar/", SessionDeleteView.as_view(), name="session_delete"),
    path("plantillas/<int:pk>/favorita/", ToggleFavoriteStyleView.as_view(), name="toggle_favorite"),
    path("plantillas/<int:pk>/reaccion/", ToggleStyleReactionView.as_view(), name="toggle_reaction"),
]
