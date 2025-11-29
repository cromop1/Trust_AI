from __future__ import annotations

import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView

from .forms import ChatSessionCreateForm, MessageForm
from .markdown_utils import render_markdown
from .models import ChatSession, Message, StyleTemplate, StyleTemplateReaction
from .services import DeepSeekClient, DeepSeekError


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "chat/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        sessions = user.chat_sessions.select_related("style_template").order_by("-updated_at")
        favorite_ids = list(user.favorite_style_templates.values_list("id", flat=True))
        total_messages = Message.objects.filter(session__user=user).count()
        total_tokens = (
            Message.objects.filter(session__user=user).aggregate(total=Sum("tokens_used")).get("total") or 0
        )

        query = (self.request.GET.get("q") or "").strip()
        styles = StyleTemplate.objects.filter(is_active=True)
        if query:
            styles = styles.filter(title__icontains=query)
        styles = styles.annotate(
            likes_count=Count(
                "style_reactions",
                filter=Q(style_reactions__value=StyleTemplateReaction.Values.LIKE),
            ),
            dislikes_count=Count(
                "style_reactions",
                filter=Q(style_reactions__value=StyleTemplateReaction.Values.DISLIKE),
            ),
            score=Coalesce(Sum("style_reactions__value"), Value(0, output_field=IntegerField())),
        ).order_by("-score", "-likes_count", "title")

        style_templates = list(styles)
        style_ids = [style.id for style in style_templates]
        reactions_map = {
            reaction.style_id: reaction.value
            for reaction in StyleTemplateReaction.objects.filter(user=user, style_id__in=style_ids)
        }
        for style in style_templates:
            style.likes_count = int(getattr(style, "likes_count", 0) or 0)
            style.dislikes_count = int(getattr(style, "dislikes_count", 0) or 0)
            style.reaction_score = int(getattr(style, "score", 0) or 0)
            style.user_reaction = reactions_map.get(style.id, 0)

        context.update(
            {
                "active_sessions": sessions[:6],
                "style_templates": style_templates,
                "favorite_ids": favorite_ids,
                "total_sessions": sessions.count(),
                "total_messages": total_messages,
                "total_tokens": total_tokens,
                "style_results_count": len(style_templates),
                "style_query": query,
            }
        )
        return context


class SessionListView(LoginRequiredMixin, ListView):
    template_name = "chat/session_list.html"
    context_object_name = "sessions"

    def get_queryset(self):
        return (
            self.request.user.chat_sessions.select_related("style_template")
            .prefetch_related("messages")
            .order_by("-updated_at")
        )


class SessionCreateView(LoginRequiredMixin, FormView):
    template_name = "chat/session_create.html"
    form_class = ChatSessionCreateForm
    success_url = reverse_lazy("chat:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["favorites_only"] = self.request.GET.get("favoritas") == "1"
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        style_id = self.request.GET.get("style")
        if style_id:
            initial["style_template"] = style_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        favorite_templates = user.favorite_style_templates.filter(is_active=True).order_by("title")
        context.update(
            {
                "favorite_templates": favorite_templates,
                "favorite_ids": list(favorite_templates.values_list("id", flat=True)),
                "showing_favorites": self.request.GET.get("favoritas") == "1",
            }
        )
        return context

    def form_valid(self, form):
        chat_session = form.save(commit=False)
        chat_session.user = self.request.user
        chat_session.save()
        Message.objects.create(
            session=chat_session,
            role=Message.Roles.SYSTEM,
            content=chat_session.style_template.system_prompt,
        )
        messages.success(self.request, "Nuevo chat creado. Empieza tu conversacion!")
        return redirect("chat:session_detail", pk=chat_session.pk)

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos antes de continuar.")
        return super().form_invalid(form)


class SessionDetailView(LoginRequiredMixin, DetailView):
    template_name = "chat/session_detail.html"
    context_object_name = "chat_session"
    model = ChatSession

    def get_queryset(self):
        return (
            ChatSession.objects.filter(user=self.request.user)
            .select_related("style_template")
            .prefetch_related("messages")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_api_key = bool((self.request.user.deepseek_api_key or "").strip())
        message_form = MessageForm()
        if not has_api_key:
            message_form.fields["content"].widget.attrs["disabled"] = "disabled"
            message_form.fields["content"].widget.attrs["placeholder"] = (
                "Agrega tu API key de DeepSeek en tu perfil para chatear."
            )
        context["message_form"] = message_form
        context["visible_messages"] = (
            self.object.messages.exclude(role=Message.Roles.SYSTEM).order_by("created_at")
        )
        context["can_chat"] = has_api_key
        return context


class SendMessageView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> HttpResponse:
        chat_session = get_object_or_404(ChatSession, pk=pk, user=request.user)

        user_api_key = (request.user.deepseek_api_key or "").strip()
        if not user_api_key:
            return JsonResponse(
                {
                    "success": False,
                    "errors": {"__all__": ["Agrega tu API key de DeepSeek en tu perfil para continuar."]},
                },
                status=403,
            )

        data = self._parse_body(request)
        form = MessageForm(data)
        if not form.is_valid():
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

        content = form.cleaned_data["content"]
        user_message = Message.objects.create(
            session=chat_session,
            role=Message.Roles.USER,
            content=content,
        )

        payload_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in chat_session.messages.order_by("created_at")
        ]
        if not any(msg["role"] == "system" for msg in payload_messages):
            payload_messages.insert(
                0,
                {
                    "role": "system",
                    "content": chat_session.style_template.system_prompt,
                },
            )

        try:
            client = DeepSeekClient(api_key=user_api_key)
            response_text, usage = client.chat_completion(
                model=chat_session.model_choice,
                messages=payload_messages,
            )
        except DeepSeekError as exc:
            user_message.delete()
            return JsonResponse(
                {
                    "success": False,
                    "errors": {"__all__": [str(exc)]},
                },
                status=502,
            )

        style_title = chat_session.style_template.title
        prefixed_response = f"Hola agente {style_title}: {response_text}".strip()

        assistant_message = Message.objects.create(
            session=chat_session,
            role=Message.Roles.ASSISTANT,
            content=prefixed_response,
            tokens_used=usage.total_tokens,
        )
        chat_session.refresh_activity()

        return JsonResponse(
            {
                "success": True,
                "assistant_message": {
                    "id": assistant_message.pk,
                    "content": assistant_message.content,
                    "content_html": render_markdown(assistant_message.content),
                    "created_at": assistant_message.created_at.isoformat(),
                },
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
            }
        )

    def _parse_body(self, request: HttpRequest):
        if request.content_type == "application/json":
            try:
                return json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return {}
        return request.POST


class SessionDeleteView(LoginRequiredMixin, View):
    template_name = "chat/session_confirm_delete.html"

    def get(self, request: HttpRequest, pk: int, *args, **kwargs) -> HttpResponse:
        chat_session = get_object_or_404(ChatSession, pk=pk, user=request.user)
        return render(request, self.template_name, {"chat_session": chat_session})

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> HttpResponse:
        chat_session = get_object_or_404(ChatSession, pk=pk, user=request.user)
        title = chat_session.title
        chat_session.delete()
        messages.success(request, f'El chat "{title}" se elimino correctamente.')
        return redirect("chat:session_list")


class ToggleFavoriteStyleView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> HttpResponse:
        style = get_object_or_404(StyleTemplate, pk=pk, is_active=True)
        user = request.user
        if style.favorite_users.filter(pk=user.pk).exists():
            style.favorite_users.remove(user)
            favored = False
        else:
            style.favorite_users.add(user)
            favored = True
        return JsonResponse(
            {
                "success": True,
                "favored": favored,
                "style_id": style.pk,
                "favorites_count": user.favorite_style_templates.count(),
            }
        )


class ToggleStyleReactionView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest, pk: int, *args, **kwargs) -> HttpResponse:
        style = get_object_or_404(StyleTemplate, pk=pk, is_active=True)
        try:
            value = int(request.POST.get("reaction"))
        except (TypeError, ValueError):
            return JsonResponse({"success": False, "error": "Reaccion invalida."}, status=400)

        if value not in (
            StyleTemplateReaction.Values.LIKE,
            StyleTemplateReaction.Values.DISLIKE,
        ):
            return JsonResponse({"success": False, "error": "Reaccion no soportada."}, status=400)

        reaction, created = StyleTemplateReaction.objects.get_or_create(
            style=style,
            user=request.user,
            defaults={"value": value},
        )

        if not created and reaction.value == value:
            reaction.delete()
            user_value = 0
        else:
            reaction.value = value
            reaction.save(update_fields=["value", "updated_at"])
            user_value = value

        aggregation = style.style_reactions.aggregate(
            likes=Count("id", filter=Q(value=StyleTemplateReaction.Values.LIKE)),
            dislikes=Count("id", filter=Q(value=StyleTemplateReaction.Values.DISLIKE)),
            score=Coalesce(Sum("value"), Value(0, output_field=IntegerField())),
        )

        return JsonResponse(
            {
                "success": True,
                "likes": aggregation.get("likes", 0),
                "dislikes": aggregation.get("dislikes", 0),
                "score": aggregation.get("score", 0),
                "user_reaction": user_value,
            }
        )
