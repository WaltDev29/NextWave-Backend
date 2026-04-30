from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from pathlib import Path
from app.core.config import settings
from app.db.database import get_db
from app.api.routers import auth, users, teams, schedules, memos, notifications, app_notifications, onboarding, ai_router

import os

def create_app() -> FastAPI:
    is_production = os.getenv("APP_ENV", "development") == "production"

    app = FastAPI(
        title="NextWave API",
        description=(
            "## NextWave 협업 플랫폼 API\n\n"
            "팀 기반의 일정 공유, 메모, 댓글, 알림 기능을 제공하는 백엔드 API입니다.\n\n"
            "### 인증 방법\n"
            "1. `/api/v1/users/signup` 으로 회원가입\n"
            "2. `/api/v1/login/access-token` 으로 로그인 후 `access_token` 획득\n"
            "3. 우측 상단 **Authorize** 버튼에 `Bearer <토큰>` 형식으로 입력"
        ),
        version="1.0.0",
        contact={"name": "NextWave Dev Team", "email": "waltdev29@gmail.com"},
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 업로드 디렉토리 자동 생성 (없으면 StaticFiles 마운트 오류 방지)
    upload_root = Path("/app/static/uploads")
    (upload_root / "users").mkdir(parents=True, exist_ok=True)
    (upload_root / "teams").mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory="/app/static"), name="static")

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
    app.include_router(notifications.router, prefix=settings.API_V1_STR)
    app.include_router(app_notifications.router, prefix=settings.API_V1_STR)
    app.include_router(ai_router, prefix=settings.API_V1_STR)

    return app
