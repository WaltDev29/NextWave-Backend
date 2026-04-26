from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.db.models import User
from app.services.llm import llm_service
from app.schemas.onboarding import OnboardingResponse

router = APIRouter(prefix="/onboarding", tags=["✨ 온보딩 (Onboarding)"])

@router.get("/guide", summary="개인화된 온보딩 가이드 데이터 조회", response_model=OnboardingResponse)
def get_onboarding_guide(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    사용자의 프로필(직업, 나이, 성별, 사용 목적)을 분석하여 
    LLM이 생성한 맞춤형 예시 일정과 메모 데이터를 반환합니다.
    """
    user_profile = {
        "job": current_user.job,
        "age": current_user.age,
        "gender": current_user.gender,
        "purpose": current_user.purpose
    }
    
    # LLM을 통해 유저 맞춤형 데이터 생성
    onboarding_data = llm_service.generate_onboarding_data(user_profile)
    
    return {
        "user_name": current_user.username,
        "guide": onboarding_data
    }
