from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os

from .database import SessionLocal
from .models import Document, Embedding

# Load environment variables
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

DEFAULT_USERNAME = os.getenv("DEFAULT_USERNAME", "user")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "password")
DEFAULT_PASSWORD_HASH = pwd_context.hash(DEFAULT_PASSWORD)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


@app.get("/api/hello")
async def read_hello():
    return {"message": "Hello from FastAPI"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username: str, password: str):
    if username != DEFAULT_USERNAME:
        return None
    if not pwd_context.verify(password, DEFAULT_PASSWORD_HASH):
        return None
    return {"username": username}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user["username"]},
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


class DocumentCreate(BaseModel):
    content: str
    embedding: List[float]


class DocumentResponse(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True


class SearchRequest(BaseModel):
    embedding: List[float]
    limit: int = 5


@app.post("/api/documents", response_model=DocumentResponse)
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    document = Document(content=doc.content)
    db.add(document)
    db.commit()
    db.refresh(document)
    embedding = Embedding(document_id=document.id, vector=doc.embedding)
    db.add(embedding)
    db.commit()
    return document


@app.get("/api/documents/{doc_id}", response_model=DocumentResponse)
def read_document(doc_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.post("/api/search")
def search_documents(req: SearchRequest, db: Session = Depends(get_db)):
    results = (
        db.query(Document)
        .join(Embedding)
        .order_by(Embedding.vector.l2_distance(req.embedding))
        .limit(req.limit)
        .all()
    )
    return {"results": [{"id": d.id, "content": d.content} for d in results]}
