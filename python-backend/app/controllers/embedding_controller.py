"""Embedding related API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Embedding
from ..views.schemas import EmbeddingOut
from ..views.transformers import embedding_to_out

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


@router.post("/demo", response_model=EmbeddingOut)
def create_demo_embedding(db: Session = Depends(get_db)):
    """Persist a demo embedding and return it."""

    vector = [0.1, 0.2, 0.3]
    embedding = Embedding(embedding=vector, content="demo content")
    db.add(embedding)
    db.commit()
    db.refresh(embedding)
    return embedding_to_out(embedding)


@router.get("/demo", response_model=List[EmbeddingOut])
def list_embeddings(
    vector: List[float] = Query(...),
    db: Session = Depends(get_db),
):
    """Return embeddings ordered by distance to the provided vector."""

    results = (
        db.query(Embedding)
        .order_by(Embedding.embedding.cosine_distance(vector))
        .all()
    )
    return [embedding_to_out(result) for result in results]
