import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
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
from backend.app.routers.analytics import router as analytics_router
from backend.app.routers.auth import router as auth_router
from backend.app.routers.chat import router as chat_router
from backend.app.routers.conversation import router as conversation_router
from backend.app.routers.documents import router as documents_router
from backend.app.routers.feedback import router as feedback_router
from backend.app.routers.user import router as user_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.messages import router as messages_router

from backend.app.services.health import run_startup_checks
from backend.app.services.admin_bootstrap import run_admin_bootstrap

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_startup_checks()
    run_admin_bootstrap()
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

# ---------- CORS Middleware (Must be added last to be outermost) ----------
default_origins = [
    "https://gcet-student-assistant-frontend.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins.strip():
    parsed_origins = [o.strip() for o in env_origins.split(",") if o.strip()]
    origins = list(set(default_origins + parsed_origins))
else:
    origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):(5173|5174|3000|8000)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(conversation_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(analytics_router)
app.include_router(health.router)
app.include_router(dashboard_router)
app.include_router(messages_router)
app.include_router(feedback_router)


@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "message": "GCET Student Assistant API is running"
    }
