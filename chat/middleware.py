from __future__ import annotations

import json

from django.http import HttpResponse

from .markdown_utils import render_markdown


class MarkdownMessageMiddleware:
    """
    Middleware que añade HTML procesado en Markdown para los mensajes
    devueltos por SendMessageView.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.path.startswith("/app/conversaciones/")
            and request.method == "POST"
            and getattr(response, "status_code", None) == 200
            and response.get("Content-Type", "").startswith("application/json")
        ):
            try:
                payload = json.loads(response.content.decode("utf-8"))
            except (ValueError, TypeError):
                return response

            assistant = payload.get("assistant_message")
            if assistant and "content" in assistant:
                assistant["content_html"] = render_markdown(assistant["content"])
                response = HttpResponse(
                    json.dumps(payload),
                    content_type="application/json",
                    status=response.status_code,
                )
        return response
