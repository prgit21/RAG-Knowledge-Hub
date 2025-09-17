"""Embedding service built on top of SentenceTransformers."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from PIL import Image
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "clip-ViT-B-32") -> None:
        self._model = SentenceTransformer(model_name)

    def encode_image(self, image: Image.Image) -> List[float]:
        return self._model.encode([image], convert_to_tensor=False)[0].tolist()

    def encode_text(self, text: str) -> List[float]:
        return self._model.encode([text], convert_to_tensor=False)[0].tolist()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


__all__ = ["EmbeddingService", "get_embedding_service"]
