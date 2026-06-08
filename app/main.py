import os
import warnings

from fastapi import FastAPI
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.chat import router as chat_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.agent import router as agent_router
from fastapi.middleware.cors import CORSMiddleware

# This silences any warning where the message module path contains "pydantic"
warnings.filterwarnings("ignore", module="pydantic")

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
    expose_headers=["X-Session-Id"],
)

# Database schema is managed by Alembic migrations ("alembic upgrade head"),
# not create_all(). See the Makefile "migrate" / "migration" targets.

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(agent_router)