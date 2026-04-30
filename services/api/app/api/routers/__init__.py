from fastapi import APIRouter
from . import auth, users, teams, schedules, memos, notifications, app_notifications, onboarding, ai_generation

# AI 관련 기능을 하나로 묶는 상위 라우터
ai_router = APIRouter(prefix="/ai")
ai_router.include_router(onboarding.router)
ai_router.include_router(ai_generation.router)
