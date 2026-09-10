from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import router
from backend.app.core.config import APP_DESCRIPTION, APP_NAME, APP_VERSION

app = FastAPI(
    title=f"{APP_NAME} API",
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

app.include_router(router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/hello")
def hello():
    return {
        "message": "Hello, CampusAI!",
        "status": "ok",
    }
