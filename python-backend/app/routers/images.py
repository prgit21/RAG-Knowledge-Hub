"""Image ingestion API routes."""

from __future__ import annotations

from typing import List, Optional, Sequence

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.images import ImageOut
from app.services.image_ingest_service import get_image_ingest_service

router = APIRouter(prefix="/api", tags=["images"])


def _vector_to_list(vector: Optional[Sequence[float]]) -> Optional[List[float]]:
    if vector is None:
        return None
    return list(vector)


@router.post("/upload-image", response_model=ImageOut)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ImageOut:
    data = await file.read()
    service = get_image_ingest_service()
    metadata = service.ingest(
        db=db,
        data=data,
        filename=file.filename or "uploaded_image",
        content_type=file.content_type,
    )
    return ImageOut(
        id=metadata.id,
        url=metadata.url,
        hash=metadata.hash,
        width=metadata.width,
        height=metadata.height,
        embedding=list(metadata.embedding) if metadata.embedding is not None else [],
        text=metadata.text,
        text_embedding=_vector_to_list(metadata.text_embedding),
    )


__all__ = ["router"]
