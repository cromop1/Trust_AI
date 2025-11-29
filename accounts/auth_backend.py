from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailBackend(ModelBackend):
    """Permite autenticación usando el correo electrónico."""

    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        UserModel = get_user_model()
        if email is None:
            email = username or kwargs.get(UserModel.EMAIL_FIELD)
        if email is None or password is None:
            return None

        try:
            user = UserModel.objects.get(Q(email__iexact=email))
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
