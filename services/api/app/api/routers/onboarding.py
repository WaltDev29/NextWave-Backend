from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api import deps
from app.db.models import User, Schedule, Memo, TeamMember, ScheduleAssignee, MemoMention
from app.services.llm import llm_service
from app.schemas.onboarding import OnboardingResponse, ContextualExampleRequest, ContextualExampleResponse
from datetime import datetime, timedelta, timezone

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
    
    # 현재 시간 (KST 기준, YYYY-MM-DDTHH:MM 형식)
    kst = timezone(timedelta(hours=9))
    current_time = datetime.now(kst).strftime("%Y-%m-%dT%H:%M")
    
    # LLM을 통해 유저 맞춤형 데이터 생성
    onboarding_data = llm_service.generate_onboarding_data(user_profile, current_time)
    
    return {
        "user_name": current_user.username,
        "guide": onboarding_data
    }

@router.post("/contextual-example", summary="맥락 기반 온보딩 예시 데이터 생성", response_model=ContextualExampleResponse)
def create_contextual_example(
    request: ContextualExampleRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    사용자와 관련된 최근 일정, 메모를 기반으로 다음 일정 혹은 메모를 생성하여 반환합니다.
    사용자가 직접 생성한 경우 또는 배정/멘션된 항목을 포함합니다.
    """
    # 1. 최근 일정 10개 가져오기
    # 사용자가 생성했거나 담당자로 등록된 일정
    schedules = (
        db.query(Schedule)
        .outerjoin(ScheduleAssignee)
        .filter(
            Schedule.team_id == request.team_id,
            or_(
                Schedule.created_by == current_user.id,
                ScheduleAssignee.user_id == current_user.id
            )
        )
        .order_by(Schedule.created_at.desc())
        .limit(10)
        .all()
    )
    
    # 2. 최근 메모 10개 가져오기
    # 사용자가 작성했거나 멘션된 메모
    memos = (
        db.query(Memo)
        .outerjoin(MemoMention)
        .filter(
            Memo.team_id == request.team_id,
            or_(
                Memo.author_id == current_user.id,
                MemoMention.user_id == current_user.id
            )
        )
        .order_by(Memo.created_at.desc())
        .limit(10)
        .all()
    )
    
    # 3. 팀 멤버 정보 가져오기 (LLM이 담당자/멘션 대상을 정할 수 있도록)
    team_members = (
        db.query(User)
        .join(TeamMember)
        .filter(TeamMember.team_id == request.team_id)
        .all()
    )
    
    # 데이터 포맷팅
    recent_schedules = [
        {
            "id": s.id, 
            "title": s.title, 
            "description": s.description,
            "start_time": s.start_time.strftime("%Y-%m-%d %H:%M") if s.start_time else None,
            "end_time": s.end_time.strftime("%Y-%m-%d %H:%M") if s.end_time else None,
            "assignee_ids": [a.user_id for a in s.assignees]
        } for s in schedules
    ]
    recent_memos = [
        {
            "id": m.id, 
            "title": m.title, 
            "content": m.content,
            "mention_ids": [mt.user_id for mt in m.mentions],
            "schedule_id": m.schedule_id
        } for m in memos
    ]
    member_list = [
        {"id": u.id, "username": u.username} for u in team_members
    ]
    
    # 현재 시간
    kst = timezone(timedelta(hours=9))
    current_time = datetime.now(kst).strftime("%Y-%m-%d %H:%M")
    
    # 4. LLM 호출
    result = llm_service.generate_contextual_example(
        part=request.part,
        recent_schedules=recent_schedules,
        recent_memos=recent_memos,
        team_members=member_list,
        current_time=current_time,
        current_user_id=current_user.id
    )
    
    return result
