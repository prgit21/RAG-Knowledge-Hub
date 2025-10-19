"""Embedding service built on top of SentenceTransformers."""

from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple

from PIL import Image
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "clip-ViT-B-32") -> None:
        self._model = SentenceTransformer(model_name)
        # Lazily initialised cache for text encodings. Using a tuple keeps
        # the cached values hashable for ``functools.lru_cache``.
        self._encode_text_cached = lru_cache(maxsize=256)(self._encode_text_impl)

    def encode_image(self, image: Image.Image) -> List[float]:
        return self._model.encode([image], convert_to_tensor=False)[0].tolist()

    def encode_text(self, text: str) -> List[float]:
        """Return the embedding vector for ``text``.

        The method applies lightweight caching so repeated queries avoid
        recomputing embeddings, significantly reducing latency for popular
        prompts. Empty or whitespace-only inputs are rejected to prevent
        unnecessary model calls.
        """

        normalized = text.strip()
        if not normalized:
            raise ValueError("text must not be empty")
        return list(self._encode_text_cached(normalized))

    def _encode_text_impl(self, text: str) -> Tuple[float, ...]:
        return tuple(
            self._model.encode([text], convert_to_tensor=False)[0].tolist()
        )


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


__all__ = ["EmbeddingService", "get_embedding_service"]
