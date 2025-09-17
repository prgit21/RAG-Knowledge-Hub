"""Utilities for composing OpenAI chat completions from retrieval results."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Sequence

import requests
from fastapi import HTTPException

from app.core.config import Settings, get_settings
from app.schemas.embeddings import RetrievedItem


DEFAULT_CHAT_MODEL = "gpt-4o-mini"


@dataclass(slots=True)
class _NormalizedItem:
    """Normalized representation of a retrieved item for prompting."""

    citation: str
    id: int
    url: str
    width: int
    height: int
    score: float
    modalities: Sequence[str]
    ocr_text: str | None


class ChatCompletionService:
    """Prepare and submit chat completion payloads based on retrieval output."""

    def __init__(self, *, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def create_completion(
        self,
        *,
        query: str,
        items: Sequence[RetrievedItem],
        model: str | None = None,
    ) -> Dict[str, Any]:
        """Call OpenAI chat completions using only retrieval-derived context."""

        normalized_items = self._normalize_items(items)
        payload = {
            "model": model or DEFAULT_CHAT_MODEL,
            "messages": self._build_messages(query=query, items=normalized_items),
        }
        return self._post(payload)

    def _normalize_items(
        self, items: Sequence[RetrievedItem]
    ) -> List[_NormalizedItem]:
        normalized: List[_NormalizedItem] = []
        for item in items:
            normalized.append(
                _NormalizedItem(
                    citation=f"cite-{item.id}",
                    id=item.id,
                    url=item.url,
                    width=item.width,
                    height=item.height,
                    score=float(item.score),
                    modalities=tuple(item.modalities_used),
                    ocr_text=self._normalize_text(item.ocr_text),
                )
            )
        return normalized

    def _normalize_text(self, text: str | None, *, max_length: int = 500) -> str | None:
        if text is None:
            return None
        collapsed = " ".join(text.split())
        if len(collapsed) <= max_length:
            return collapsed
        return f"{collapsed[: max_length - 1]}…"

    def _build_messages(
        self,
        *,
        query: str,
        items: Sequence[_NormalizedItem],
    ) -> List[Dict[str, str]]:
        context = self._format_context(items)
        user_content = (
            "You are given search results retrieved from an image knowledge base. "
            "Answer the user's question using only the information present in the "
            "context. If the context does not contain the answer, respond that the "
            "information is unavailable. Include citations using the provided "
            "[cite-<id>] markers for any referenced facts.\n\n"
            f"Question: {query}\n\nContext:\n{context}"
        )
        return [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant constrained to answer strictly "
                    "from provided retrieval context."
                ),
            },
            {"role": "user", "content": user_content},
        ]

    def _format_context(self, items: Sequence[_NormalizedItem]) -> str:
        if not items:
            return "(no retrieval results available)"
        sections: List[str] = []
        for item in items:
            modalities = ", ".join(item.modalities) if item.modalities else "none"
            text_line = item.ocr_text or "(no text available)"
            sections.append(
                "\n".join(
                    [
                        f"[{item.citation}] id: {item.id}",
                        f"url: {item.url}",
                        f"dimensions: {item.width}x{item.height}",
                        f"score: {item.score:.4f}",
                        f"modalities: {modalities}",
                        f"text: {text_line}",
                    ]
                )
            )
        return "\n\n".join(sections)

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        api_key = self._settings.openai_api_key
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            self._settings.openai_chat_api_url,
            headers=headers,
            json=payload,
            timeout=30,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()


@lru_cache
def get_chat_completion_service() -> ChatCompletionService:
    return ChatCompletionService()


__all__ = ["ChatCompletionService", "get_chat_completion_service"]
