from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os

from .db import Base, engine, SessionLocal, get_db
from .models import Embedding, User
from .schemas import Token, EmbeddingOut

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(User).filter(User.username == "user").first():
        db.add(User(username="user", hashed_password=pwd_context.hash("password")))
        db.commit()
    db.close()


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
    embedding = Embedding(embedding=vector)
    db.add(embedding)
    db.commit()
    db.refresh(embedding)
    return {"id": embedding.id, "embedding": list(embedding.embedding)}


@app.get("/api/embeddings/demo", response_model=List[EmbeddingOut])
def list_embeddings(
    vector: List[float] = Query(...), db: Session = Depends(get_db)
):
    results = (
        db.query(Embedding)
        .order_by(Embedding.embedding.cosine_distance(vector))
        .all()
    )
    return [{"id": e.id, "embedding": list(e.embedding)} for e in results]
