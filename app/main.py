import os

from fastapi import FastAPI
from app.db.init_db import init_db
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=os.getenv("APP_NAME", "Pharma Guide API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(chat_router)