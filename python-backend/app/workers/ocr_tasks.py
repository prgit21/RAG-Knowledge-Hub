"""Background task helpers for OCR processing."""

from __future__ import annotations

from typing import Optional

from PIL import Image

from app.services.ocr_service import get_ocr_service


def extract_text_from_image(image: Image.Image) -> Optional[str]:
    """Extract OCR text using the shared OCR service."""

    return get_ocr_service().extract_text(image)


__all__ = ["extract_text_from_image"]
