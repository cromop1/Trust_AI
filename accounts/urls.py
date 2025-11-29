from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import EmailLoginView, ProfileView, SignUpView

app_name = "accounts"

urlpatterns = [
    path("registro/", SignUpView.as_view(), name="signup"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="accounts:login"), name="logout"),
    path("perfil/", ProfileView.as_view(), name="profile"),
]
