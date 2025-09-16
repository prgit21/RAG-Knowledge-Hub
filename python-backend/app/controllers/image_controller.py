"""Image upload and processing endpoints."""

import hashlib
import uuid
from io import BytesIO
from typing import List, Optional

import numpy as np
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from ..core.clients import clip_model, minio_client, ocr_reader
from ..core.config import MINIO_BUCKET, MINIO_ENDPOINT, MINIO_SECURE
from ..db import get_db
from ..models import ImageMetadata
from ..views.schemas import ImageOut
from ..views.transformers import image_to_out

router = APIRouter(prefix="/api", tags=["images"])


@router.post("/upload-image", response_model=ImageOut)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Store an uploaded image, persist its metadata and return the record."""

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    object_name = f"{uuid.uuid4()}_{file.filename}"
    minio_client.put_object(
        MINIO_BUCKET,
        object_name,
        BytesIO(data),
        length=len(data),
        content_type=file.content_type,
    )

    image = Image.open(BytesIO(data)).convert("RGB")
    width, height = image.size
    hash_value = hashlib.sha256(data).hexdigest()
    scheme = "https" if MINIO_SECURE else "http"
    url = f"{scheme}://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"

    image_embedding_vector = (
        clip_model.encode([image], convert_to_tensor=False)[0].tolist()
    )

    ocr_text: Optional[str] = None
    text_embedding_vector: Optional[List[float]] = None
    try:
        ocr_results = ocr_reader.readtext(np.array(image), detail=0)
        text_parts = [result for result in ocr_results if result]
        if text_parts:
            ocr_text = " ".join(text_parts).strip()
    except Exception:  # pragma: no cover - protective fallback
        ocr_text = None

    if ocr_text:
        text_embedding_vector = (
            clip_model.encode([ocr_text], convert_to_tensor=False)[0].tolist()
        )

    metadata = ImageMetadata(
        url=url,
        hash=hash_value,
        width=width,
        height=height,
        embedding=image_embedding_vector,
        text=ocr_text,
        text_embedding=text_embedding_vector,
    )
    db.add(metadata)
    db.commit()
    db.refresh(metadata)

    return image_to_out(metadata)
