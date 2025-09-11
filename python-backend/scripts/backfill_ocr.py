from minio import Minio
from app.main import clip_model, text_model, pytesseract, MINIO_BUCKET, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE
from app.models import ImageMetadata
from app.db import SessionLocal
from PIL import Image
from io import BytesIO
import hashlib

client = Minio(MINIO_ENDPOINT,
               access_key=MINIO_ACCESS_KEY,
               secret_key=MINIO_SECRET_KEY,
               secure=MINIO_SECURE)
session = SessionLocal()
for obj in client.list_objects(MINIO_BUCKET, recursive=True):
    data = client.get_object(MINIO_BUCKET, obj.object_name).read()
    image = Image.open(BytesIO(data))
    hash_value = hashlib.sha256(data).hexdigest()
    url = f"{'https' if MINIO_SECURE else 'http'}://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{obj.object_name}"

    ocr_text = pytesseract.image_to_string(image) if pytesseract else ""
    text_vec = (text_model.encode([ocr_text], convert_to_tensor=False)[0].tolist()
                if ocr_text.strip() else None)

    metadata = session.query(ImageMetadata).filter_by(url=url).first()
    if metadata:
        metadata.text = ocr_text
        metadata.text_embedding = text_vec
    else:
        width, height = image.size
        embedding = clip_model.encode([image], convert_to_tensor=False)[0]
        metadata = ImageMetadata(
            url=url, hash=hash_value, width=width, height=height,
            embedding=embedding.tolist(), text=ocr_text,
            text_embedding=text_vec
        )
        session.add(metadata)
    session.commit()
