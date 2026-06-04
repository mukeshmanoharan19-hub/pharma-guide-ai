from fastapi import FastAPI
from app.db.init_db import init_db
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router

app = FastAPI(
    title="Medicine AI Assistant"
)

init_db()

app.include_router(auth_router)
app.include_router(health_router)