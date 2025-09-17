"""MinIO storage helpers."""

from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from typing import Optional

from minio import Minio

from app.core.config import Settings, get_settings


class MinioStorageClient:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._client = Minio(
            self._settings.minio_endpoint,
            access_key=self._settings.minio_access_key,
            secret_key=self._settings.minio_secret_key,
            secure=self._settings.minio_secure,
        )

    @property
    def bucket(self) -> str:
        return self._settings.minio_bucket

    def ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self.bucket):
            self._client.make_bucket(self.bucket)

    def upload_file(
        self, object_name: str, data: bytes, content_type: Optional[str]
    ) -> str:
        self._client.put_object(
            self.bucket,
            object_name,
            BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return self.object_url(object_name)

    def object_url(self, object_name: str) -> str:
        scheme = "https" if self._settings.minio_secure else "http"
        return f"{scheme}://{self._settings.minio_endpoint}/{self.bucket}/{object_name}"

    @property
    def client(self) -> Minio:
        return self._client


@lru_cache
def get_storage_client() -> MinioStorageClient:
    return MinioStorageClient()


__all__ = ["MinioStorageClient", "get_storage_client"]
