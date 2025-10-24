"""Amazon S3 storage helpers."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from urllib.parse import urlparse

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from app.core.config import Settings, get_settings


class S3StorageClient:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        client_kwargs: dict[str, Optional[str]] = {
            "region_name": self._settings.s3_region,
            "endpoint_url": self._settings.s3_endpoint_url,
        }
        if self._settings.s3_access_key_id:
            client_kwargs["aws_access_key_id"] = self._settings.s3_access_key_id
        if self._settings.s3_secret_access_key:
            client_kwargs["aws_secret_access_key"] = (
                self._settings.s3_secret_access_key
            )
        # Remove ``None`` values so boto3 falls back to its default credential chain.
        filtered_kwargs = {
            key: value for key, value in client_kwargs.items() if value is not None
        }
        self._client = boto3.client("s3", **filtered_kwargs)

    @property
    def bucket(self) -> str:
        return self._settings.s3_bucket

    def ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self.bucket)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code not in {"404", "NoSuchBucket"}:
                raise
            create_kwargs: dict[str, object] = {"Bucket": self.bucket}
            region = self._settings.s3_region
            if region and region != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {
                    "LocationConstraint": region
                }
            self._client.create_bucket(**create_kwargs)

    def upload_file(
        self, object_name: str, data: bytes, content_type: Optional[str]
    ) -> str:
        put_object_kwargs: dict[str, object] = {
            "Bucket": self.bucket,
            "Key": object_name,
            "Body": data,
        }
        if content_type:
            put_object_kwargs["ContentType"] = content_type
        self._client.put_object(**put_object_kwargs)
        return self.object_url(object_name)

    def object_url(self, object_name: str) -> str:
        endpoint = self._settings.s3_endpoint_url
        if endpoint:
            base = endpoint.rstrip("/")
            if self._settings.s3_use_path_style:
                return f"{base}/{self.bucket}/{object_name}"
            parsed = urlparse(base)
            netloc = parsed.netloc or base.split("//")[-1]
            scheme = parsed.scheme or "https"
            return f"{scheme}://{self.bucket}.{netloc}/{object_name}"

        region = self._settings.s3_region
        if region and region != "us-east-1":
            return f"https://{self.bucket}.s3.{region}.amazonaws.com/{object_name}"
        return f"https://{self.bucket}.s3.amazonaws.com/{object_name}"

    @property
    def client(self) -> BaseClient:
        return self._client


@lru_cache
def get_storage_client() -> S3StorageClient:
    return S3StorageClient()


__all__ = ["S3StorageClient", "get_storage_client"]
