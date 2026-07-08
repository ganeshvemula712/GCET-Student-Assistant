from fastapi import FastAPI

from backend.app.routers.chat import router as chat_router


app = FastAPI(
    title="GCET Student Assistant API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to GCET Student Assistant API"
    }


app.include_router(chat_router)