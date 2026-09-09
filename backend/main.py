from fastapi import FastAPI

from backend.app.api.routes import router
from backend.app.core.config import APP_DESCRIPTION, APP_NAME, APP_VERSION

app = FastAPI(
    title=f"{APP_NAME} API",
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

app.include_router(router)


@app.get("/hello")
def hello():
    return {
        "message": "Hello, CampusAI!",
        "status": "ok",
    }