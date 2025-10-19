"""Search and embedding related API routes."""

from __future__ import annotations

from typing import List

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.images_repo import EmbeddingRepository
from app.core.security import get_current_user
from app.schemas.embeddings import (
    EmbeddingOut,
    OpenAIRequest,
    RetrieveQuery,
    RetrievedItem,
    RetrievalAugmentedResponse,
)
from app.services.retrieval_service import (
    RetrievalService,
    RetrievalServiceError,
    get_retrieval_service,
)
from app.services.chat_completion_service import (
    ChatCompletionService,
    get_chat_completion_service,
)

router = APIRouter(
    prefix="/api", tags=["search"], dependencies=[Depends(get_current_user)]
)


@router.post("/embeddings/demo", response_model=EmbeddingOut)
def create_demo_embedding(db: Session = Depends(get_db)) -> EmbeddingOut:
    repository = EmbeddingRepository(db)
    embedding = repository.create(embedding=[0.1, 0.2, 0.3], content="demo content")
    return EmbeddingOut(
        id=embedding.id,
        embedding=list(embedding.embedding),
        content=embedding.content,
    )


@router.get("/embeddings/demo", response_model=List[EmbeddingOut])
def list_embeddings(
    vector: List[float] = Query(...),
    db: Session = Depends(get_db),
) -> List[EmbeddingOut]:
    repository = EmbeddingRepository(db)
    results = repository.search_by_vector(vector)
    return [
        EmbeddingOut(
            id=record.id,
            embedding=list(record.embedding),
            content=record.content,
        )
        for record in results
    ]


@router.post("/openai")
def call_openai(request: OpenAIRequest) -> dict:
    settings = get_settings()
    api_key = settings.openai_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": request.model, "input": request.input}
    response = requests.post(settings.openai_api_url, headers=headers, json=payload, timeout=30)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@router.post("/search/retrieve", response_model=RetrievalAugmentedResponse)
def retrieve_images(
    request: RetrieveQuery,
    db: Session = Depends(get_db),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    chat_service: ChatCompletionService = Depends(get_chat_completion_service),
) -> RetrievalAugmentedResponse:
    try:
        results = retrieval_service.retrieve(db=db, query=request.query, k=request.k)
    except RetrievalServiceError as exc:
        status_code = 400 if isinstance(exc.__cause__, ValueError) else 503
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    items = [
        RetrievedItem(
            id=result.metadata.id,
            url=result.metadata.url,
            width=result.metadata.width,
            height=result.metadata.height,
            score=result.score,
            ocr_text=result.metadata.text,
            modalities_used=result.modalities,
            distances=result.distances,
            similarities=result.similarities,
        )
        for result in results
    ]

    completion = chat_service.create_completion(query=request.query, items=items)

    return RetrievalAugmentedResponse(items=items, completion=completion)


__all__ = ["router"]
