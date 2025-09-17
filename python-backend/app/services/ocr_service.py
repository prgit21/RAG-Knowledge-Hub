"""OCR service leveraging EasyOCR."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable, Optional

import easyocr
import numpy as np
from PIL import Image


class OCRService:
    def __init__(self, languages: Iterable[str] | None = None, gpu: bool = False) -> None:
        self._reader = easyocr.Reader(list(languages or ["en"]), gpu=gpu)

    def extract_text(self, image: Image.Image) -> Optional[str]:
        try:
            results = self._reader.readtext(np.array(image), detail=0)
        except Exception:  # pragma: no cover - library level guard
            return None
        parts = [
            part.strip()
            for part in results
            if isinstance(part, str) and part and part.strip()
        ]
        return " ".join(parts) if parts else None


@lru_cache
def get_ocr_service() -> OCRService:
    return OCRService()


__all__ = ["OCRService", "get_ocr_service"]
