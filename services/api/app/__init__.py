from fastapi import FastAPI
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    @app.get("/")
    def read_root():
        return {"message": "Welcome to NextWave API"}

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app
