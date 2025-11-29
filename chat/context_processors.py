from __future__ import annotations

from typing import Dict

from django.db.models import Count


def chat_sidebar(request) -> Dict[str, object]:
    resolver = getattr(request, "resolver_match", None)
    if request.user.is_authenticated and (not resolver or resolver.namespace != "pages"):
        recent_sessions = (
            request.user.chat_sessions.select_related("style_template")
            .annotate(message_count=Count("messages"))
            .order_by("-updated_at")[:8]
        )
        return {
            "recent_chat_sessions": recent_sessions,
        }
    return {"recent_chat_sessions": []}
