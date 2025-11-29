from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from .forms import (
    EmailAuthenticationForm,
    UserProfileForm,
    UserRegistrationForm,
)


class SignUpView(FormView):
    template_name = "accounts/signup.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("chat:dashboard")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend="accounts.auth_backend.EmailBackend")
        messages.success(self.request, "Tu cuenta ha sido creada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "No se pudo crear la cuenta. Revisa los errores.")
        return super().form_invalid(form)


class EmailLoginView(FormView):
    template_name = "accounts/login.html"
    form_class = EmailAuthenticationForm
    success_url = reverse_lazy("chat:dashboard")

    def get_success_url(self):
        redirect_to = self.request.POST.get("next") or self.request.GET.get("next")
        if redirect_to:
            return redirect_to
        return super().get_success_url()

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, "Sesión iniciada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "No se pudo iniciar sesión. Revisa tus credenciales.")
        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"
    form_class = UserProfileForm

    def get_context_data(self, request, form=None):
        form = form or self.form_class(instance=request.user)
        return {"form": form}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(request))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("accounts:profile")
        messages.error(request, "Corrige los errores antes de guardar.")
        return render(
            request,
            self.template_name,
            self.get_context_data(request, form=form),
        )
