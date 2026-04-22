from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.db.database import get_db
from app.api.routers import auth, users, teams, schedules, memos

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def read_root():
        return {"message": "Welcome to NextWave API"}

    @app.get("/health")
    def health_check(db: Session = Depends(get_db)):
        try:
            # DB 연결이 정상인지 확인하기 위한 가장 단순한 쿼리
            db.execute(text("SELECT 1"))
            return {"status": "ok", "database": "connected"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB Connection failed: {str(e)}")

    # 신규 라우터 등록
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(users.router, prefix=settings.API_V1_STR)
    app.include_router(teams.router, prefix=settings.API_V1_STR)
    app.include_router(schedules.router, prefix=settings.API_V1_STR)
    app.include_router(schedules.team_schedules_router, prefix=settings.API_V1_STR)
    app.include_router(memos.router, prefix=settings.API_V1_STR)
    app.include_router(memos.team_memos_router, prefix=settings.API_V1_STR)
    app.include_router(memos.schedule_memos_router, prefix=settings.API_V1_STR)

    return app
