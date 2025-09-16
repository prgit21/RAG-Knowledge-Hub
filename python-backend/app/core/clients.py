"""Shared external service clients and heavy resources."""

import easyocr
from minio import Minio
from sentence_transformers import SentenceTransformer

from .config import (
    MINIO_ACCESS_KEY,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
)

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)

clip_model = SentenceTransformer("clip-ViT-B-32")
ocr_reader = easyocr.Reader(["en"], gpu=False)

__all__ = ["clip_model", "minio_client", "ocr_reader"]
