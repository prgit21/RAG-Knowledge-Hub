"""Database access helpers for image and embedding records."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.embeddings import Embedding
from app.models.images import ImageMetadata


class ImageRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        url: str,
        hash_value: str,
        width: int,
        height: int,
        embedding: List[float],
        text: Optional[str] = None,
        text_embedding: Optional[List[float]] = None,
    ) -> ImageMetadata:
        metadata = ImageMetadata(
            url=url,
            hash=hash_value,
            width=width,
            height=height,
            embedding=embedding,
            text=text,
            text_embedding=text_embedding,
        )
        self._session.add(metadata)
        self._session.commit()
        self._session.refresh(metadata)
        return metadata


class EmbeddingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, embedding: List[float], content: Optional[str] = None) -> Embedding:
        record = Embedding(embedding=embedding, content=content)
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return record

    def search_by_vector(self, vector: List[float]) -> List[Embedding]:
        return (
            self._session.query(Embedding)
            .order_by(Embedding.embedding.cosine_distance(vector))
            .all()
        )


__all__ = ["ImageRepository", "EmbeddingRepository"]
