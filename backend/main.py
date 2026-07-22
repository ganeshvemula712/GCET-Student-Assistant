from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from backend.app.core.config import APP_NAME
from backend.app.core.database import Base, engine
from backend.app.core.handlers import register_exception_handlers
from backend.app.core.logging import log_requests
from backend.app.core.rate_limiter import limiter

# Models
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message

# Routers
from backend.app.routers import health
from backend.app.routers.admin import router as admin_router
from backend.app.routers.auth import router as auth_router
from backend.app.routers.chat import router as chat_router
from backend.app.routers.conversation import router as conversation_router
from backend.app.routers.documents import router as documents_router
from backend.app.routers.user import router as user_router

from backend.app.services.health import run_startup_checks

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_startup_checks()
    yield


app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    summary="AI-powered student assistant for GCET.",
    description="""
# GCET Student Assistant API

An AI-powered backend built using FastAPI, PostgreSQL,
ChromaDB and Google Gemini.
""",
    lifespan=lifespan,
)

# ---------- Rate Limiter ----------
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.add_middleware(SlowAPIMiddleware)

# ---------- Logging ----------
app.middleware("http")(log_requests)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(conversation_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(health.router)


@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "message": "GCET Student Assistant API is running"
    }