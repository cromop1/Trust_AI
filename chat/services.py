from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover - fallback when requests is missing
    requests = None  # type: ignore

from django.conf import settings


class DeepSeekError(Exception):
    """Raised when the DeepSeek API returns an error or cannot be reached."""


@dataclass(slots=True)
class DeepSeekUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


MODEL_ALIAS = {
    "trustai-chat": "deepseek-chat",
    "trustai-coder": "deepseek-coder",
    "trustai-reasoner": "deepseek-reasoner",
}


class DeepSeekClient:
    BASE_URL = "https://api.deepseek.com"
    COMPLETIONS_PATH = "/v1/chat/completions"

    def __init__(self, api_key: str | None = None, timeout: int | None = None):
        if requests is None:
            raise DeepSeekError("Instala la librería 'requests' (pip install requests) para usar la API de DeepSeek.")
        configured_key = getattr(settings, "DEEPSEEK_API_KEY", None)
        self.api_key = api_key or configured_key
        if not self.api_key:
            raise DeepSeekError("No se ha configurado la variable DEEPSEEK_API_KEY.")
        self.timeout = timeout or getattr(settings, "DEEPSEEK_TIMEOUT", 40)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _endpoint(self, model: str) -> str:
        return self.COMPLETIONS_PATH

    def chat_completion(
        self,
        *,
        model: str,
        messages: Iterable[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> tuple[str, DeepSeekUsage]:
        api_model = MODEL_ALIAS.get(model, model)

        payload: Dict[str, Any] = {
            "model": api_model,
            "messages": list(messages),
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = requests.post(  # type: ignore[union-attr]
                f"{self.BASE_URL}{self._endpoint(api_model)}",
                json=payload,
                timeout=self.timeout,
                headers=self._headers(),
            )
        except Exception as exc:  # broad to cover missing dependency dynamic attribute
            if requests is not None and isinstance(exc, requests.RequestException):  # type: ignore[attr-defined]
                detail = getattr(exc, "response", None)
                message = "No se pudo conectar con la API de DeepSeek."
                if detail is not None and getattr(detail, "text", ""):
                    message = f"{message} Detalle: {detail.text}"
                raise DeepSeekError(message) from exc
            raise DeepSeekError("No se pudo conectar con la API de DeepSeek.") from exc

        if response.status_code >= 400:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            raise DeepSeekError(f"DeepSeek error ({response.status_code}): {detail}")

        data = response.json()
        choices: List[Dict[str, Any]] = data.get("choices", [])
        if not choices:
            raise DeepSeekError("La API de DeepSeek no devolvió resultados.")

        message = choices[0].get("message", {})
        content = message.get("content")
        if not content:
            raise DeepSeekError("La respuesta de DeepSeek no contiene contenido.")

        usage_data = data.get("usage", {})
        usage = DeepSeekUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        return content, usage
