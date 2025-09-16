"""Helpers for translating database models into API schemas."""

from ..models import Embedding, ImageMetadata
from .schemas import EmbeddingOut, ImageOut


def embedding_to_out(entity: Embedding) -> EmbeddingOut:
    """Convert an :class:`Embedding` instance into its API representation."""

    return EmbeddingOut(
        id=entity.id,
        embedding=list(entity.embedding) if entity.embedding is not None else [],
        content=entity.content,
    )


def image_to_out(entity: ImageMetadata) -> ImageOut:
    """Convert an :class:`ImageMetadata` instance into its API representation."""

    return ImageOut(
        id=entity.id,
        url=entity.url,
        hash=entity.hash,
        width=entity.width,
        height=entity.height,
        embedding=list(entity.embedding) if entity.embedding is not None else [],
        text=entity.text,
        text_embedding=(
            list(entity.text_embedding) if entity.text_embedding is not None else None
        ),
    )
