"""Hybrid multimodal retrieval service."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, Sequence

from sqlalchemy.orm import Session

from app.models.images import ImageMetadata
from app.repositories.images_repo import ImageRepository
from app.services.embedding_service import (
    EmbeddingService,
    get_embedding_service,
)


VISUAL_MODALITY = "visual"
OCR_MODALITY = "ocr"


@dataclass
class RetrievalResult:
    """Container for a hybrid retrieval result."""

    metadata: ImageMetadata
    score: float
    modalities: List[str]
    distances: Dict[str, float]
    similarities: Dict[str, float]


class RetrievalService:
    """Service that performs weighted blending across retrieval modalities."""

    _WEIGHTS: Dict[str, float] = {
        VISUAL_MODALITY: 0.6,
        OCR_MODALITY: 0.4,
    }

    def __init__(self, embedding_service: EmbeddingService) -> None:
        self._embedding_service = embedding_service

    def retrieve(
        self,
        *,
        db: Session,
        query: str,
        k: int = 3,
    ) -> List[RetrievalResult]:
        """Return the top-k multimodal matches for the provided query."""

        if k <= 0:
            return []

        query_vector = self._embedding_service.encode_text(query)
        repository = ImageRepository(db)

        pool_size = max(k * 2, k)
        visual_candidates = repository.search_by_embedding_vector(
            query_vector, limit=pool_size
        )
        text_candidates = repository.search_by_text_embedding_vector(
            query_vector, limit=pool_size
        )

        aggregated = self._merge_candidates(visual_candidates, text_candidates)
        results = self._rank_results(aggregated)
        return results[:k]

    def _merge_candidates(
        self,
        visual_candidates: Sequence[tuple[ImageMetadata, float]],
        text_candidates: Sequence[tuple[ImageMetadata, float]],
    ) -> Dict[int, Dict[str, object]]:
        """Merge the ANN candidate pools into a single structure."""

        aggregated: Dict[int, Dict[str, object]] = {}

        for metadata, distance in visual_candidates:
            self._update_entry(
                aggregated,
                metadata,
                VISUAL_MODALITY,
                distance,
            )

        for metadata, distance in text_candidates:
            self._update_entry(
                aggregated,
                metadata,
                OCR_MODALITY,
                distance,
            )

        return aggregated

    def _update_entry(
        self,
        aggregated: Dict[int, Dict[str, object]],
        metadata: ImageMetadata,
        modality: str,
        distance: float,
    ) -> None:
        similarity = 1.0 - float(distance)

        entry = aggregated.setdefault(
            metadata.id,
            {
                "metadata": metadata,
                "modalities": set(),
                "distances": {},
                "similarities": {},
            },
        )

        entry["metadata"] = metadata
        entry["modalities"].add(modality)
        entry["distances"][modality] = float(distance)
        entry["similarities"][modality] = similarity

    def _rank_results(
        self, aggregated: Dict[int, Dict[str, object]]
    ) -> List[RetrievalResult]:
        """Blend modality scores and rank the resulting items."""

        results: List[RetrievalResult] = []
        for entry in aggregated.values():
            metadata = entry["metadata"]
            modalities: Iterable[str] = entry["modalities"]
            distances: Dict[str, float] = entry["distances"]
            similarities: Dict[str, float] = entry["similarities"]

            combined_score = self._blend_scores(modalities, similarities)
            results.append(
                RetrievalResult(
                    metadata=metadata,
                    score=combined_score,
                    modalities=sorted(modalities),
                    distances=dict(distances),
                    similarities=dict(similarities),
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)
        return results

    def _blend_scores(
        self,
        modalities: Iterable[str],
        similarities: Dict[str, float],
    ) -> float:
        weights = [self._WEIGHTS.get(modality, 0.0) for modality in modalities]
        total_weight = sum(weights)
        if total_weight <= 0:
            return 0.0
        weighted_sum = sum(
            similarities.get(modality, 0.0) * self._WEIGHTS.get(modality, 0.0)
            for modality in modalities
        )
        return weighted_sum / total_weight


@lru_cache
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(embedding_service=get_embedding_service())


__all__ = [
    "RetrievalResult",
    "RetrievalService",
    "get_retrieval_service",
]
