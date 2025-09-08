"""Utility functions for interacting with MinIO storage.

This module exposes a small set of helpers that can be reused by FastAPI
endpoints or other modules. It reads configuration from environment variables
and provides convenience wrappers for uploading objects and generating
presigned URLs.

Environment variables:

* ``MINIO_ENDPOINT``   – MinIO server host (optionally including scheme).
* ``MINIO_ACCESS_KEY`` – Access key for authentication.
* ``MINIO_SECRET_KEY`` – Secret key for authentication.
* ``MINIO_BUCKET``     – Bucket where objects will be stored.

The two primary functions intended for external use are :func:`upload_image`
and :func:`get_presigned_url`.
"""

from __future__ import annotations

import os
from datetime import timedelta
from io import BytesIO
from typing import Union

from fastapi import UploadFile
from minio import Minio


_client: Minio | None = None
_bucket_name: str | None = None


def _get_env(name: str) -> str:
    """Fetch a required environment variable or raise a ``KeyError``."""

    value = os.environ.get(name)
    if not value:
        raise KeyError(f"Missing environment variable: {name}")
    return value


def init_minio_client() -> Minio:
    """Initialise and return a global :class:`~minio.Minio` client.

    The client and bucket name are cached after the first call.
    """

    global _client, _bucket_name
    if _client is None:
        endpoint = _get_env("MINIO_ENDPOINT")
        access_key = _get_env("MINIO_ACCESS_KEY")
        secret_key = _get_env("MINIO_SECRET_KEY")
        _bucket_name = _get_env("MINIO_BUCKET")

        # Determine whether to use TLS based on the endpoint scheme. The MinIO
        # constructor expects the host without the scheme.
        secure = not endpoint.startswith("http://")
        endpoint = endpoint.replace("http://", "").replace("https://", "")

        _client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

        if not _client.bucket_exists(_bucket_name):
            _client.make_bucket(_bucket_name)

    return _client


def upload_image(object_name: str, data: Union[bytes, UploadFile]) -> str:
    """Upload ``data`` to MinIO under ``object_name``.

    ``data`` may be raw bytes or an :class:`~fastapi.UploadFile` instance. The
    function returns the name of the stored object.
    """

    client = init_minio_client()

    if isinstance(data, UploadFile):
        # Read the uploaded file into memory before sending to MinIO.
        content = data.file.read()
    elif isinstance(data, bytes):
        content = data
    else:
        raise TypeError("data must be bytes or UploadFile")

    stream = BytesIO(content)
    client.put_object(_bucket_name, object_name, stream, length=len(content))
    return object_name


def get_presigned_url(object_name: str, expires: int = 3600) -> str:
    """Generate a presigned URL for ``object_name``.

    Parameters
    ----------
    object_name:
        Name of the object in the configured bucket.
    expires:
        Expiration time in seconds for the generated URL (default 1 hour).
    """

    client = init_minio_client()
    return client.presigned_get_object(
        _bucket_name, object_name, expires=timedelta(seconds=expires)
    )


__all__ = ["init_minio_client", "upload_image", "get_presigned_url"]

