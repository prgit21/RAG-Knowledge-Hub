from datetime import datetime, timedelta
from typing import List, Optional
import requests
import hashlib

from fastapi import Depends, FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from minio import Minio
from io import BytesIO
import uuid
from PIL import Image
from sentence_transformers import SentenceTransformer

from .db import Base, engine, SessionLocal, get_db
from .models import Embedding, User, ImageMetadata
from .schemas import (
    OpenAIRequest,
    Token,
    EmbeddingOut,
    AskRequest,
    AskResponse,
    ImageOut,
)

# Load environment variables
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9001")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "images")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)

clip_model = SentenceTransformer("clip-ViT-B-32")


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://localhost:4200",
        "http://localhost:4201",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(User).filter(User.username == "user").first():
        db.add(User(username="user", hashed_password=pwd_context.hash("password")))
        db.commit()
    db.close()
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)


@app.get("/api/hello")
async def read_hello():
    return {"message": "Hello from FastAPI"}


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


@app.post("/api/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": f"Hello, {username}"}


@app.post("/api/embeddings/demo", response_model=EmbeddingOut)
def create_demo_embedding(db: Session = Depends(get_db)):
    vector = [0.1, 0.2, 0.3]
    embedding = Embedding(embedding=vector, content="demo content")
    db.add(embedding)
    db.commit()
    db.refresh(embedding)
    return {"id": embedding.id, "embedding": list(embedding.embedding), "content": embedding.content}


@app.get("/api/embeddings/demo", response_model=List[EmbeddingOut])
def list_embeddings(
    vector: List[float] = Query(...), db: Session = Depends(get_db)
):
    results = (
        db.query(Embedding)
        .order_by(Embedding.embedding.cosine_distance(vector))
        .all()
    )
    return [
        {"id": e.id, "embedding": list(e.embedding), "content": e.content}
        for e in results
    ]


@app.post("/api/upload-image", response_model=ImageOut)
async def upload_image(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    data = await file.read()
    object_name = f"{uuid.uuid4()}_{file.filename}"
    minio_client.put_object(
        MINIO_BUCKET,
        object_name,
        BytesIO(data),
        length=len(data),
        content_type=file.content_type,
    )
    image = Image.open(BytesIO(data))
    width, height = image.size
    hash_value = hashlib.sha256(data).hexdigest()
    url = f"{'https' if MINIO_SECURE else 'http'}://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"
    embedding = clip_model.encode([image], convert_to_tensor=False)[0]
    metadata = ImageMetadata(
        url=url,
        hash=hash_value,
        width=width,
        height=height,
        embedding=embedding.tolist(),
    )
    db.add(metadata)
    db.commit()
    db.refresh(metadata)
    image_out = ImageOut(
        id=metadata.id,
        url=metadata.url,
        hash=metadata.hash,
        width=metadata.width,
        height=metadata.height,
        embedding=list(metadata.embedding) if metadata.embedding is not None else [],
        text=metadata.text,
        text_embedding=(
            list(metadata.text_embedding)
            if metadata.text_embedding is not None
            else None
        ),
    )
    return image_out


@app.post("/api/openai")
def call_openai(request: OpenAIRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": request.model, "input": request.input}
    response = requests.post(
        "https://api.openai.com/v1/responses", headers=headers, json=payload
    )
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
