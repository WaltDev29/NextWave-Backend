from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import Schedule, ScheduleAssignee, User, TeamMember, RoleEnum
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleStatusUpdate,
    ScheduleResponse,
    ScheduleAssigneeCreate,
    ScheduleAssigneeResponse
)

router = APIRouter(prefix="/schedules", tags=["🗓️ 일정 (Schedules)"])
team_schedules_router = APIRouter(prefix="/teams", tags=["🗓️ 일정 (Schedules)"])

_401 = {401: {"description": "인증 토큰 없음 또는 만료"}}
_403 = {403: {"description": "해당 팀의 소속 멤버가 아니거나 권한 부족"}}
_404 = {404: {"description": "일정을 찾을 수 없음"}}

# =======================================================
# 팀 라우터 파트 (/teams/{team_id}/schedules)
# =======================================================
@team_schedules_router.get("/{team_id}/schedules", response_model=List[ScheduleResponse],
    summary="팀 일정 전체 조회", responses={**_401, **_403})
def get_team_schedules(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """해당 팀에 등록된 모든 일정 조회"""
    deps.check_team_membership(db, team_id, current_user.id)
    return db.query(Schedule).filter(Schedule.team_id == team_id).all()

# =======================================================
# 스케쥴 단건 및 수정 파트 (/schedules)
# =======================================================
@router.post("/", response_model=ScheduleResponse, summary="일정 생성", responses={**_401, **_403})
def create_schedule(
    *,
    db: Session = Depends(deps.get_db),
    schedule_in: ScheduleCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """일정 신규 생성 (guest 권한은 팀 일정 생성 불가)"""
    deps.check_team_membership(
        db, schedule_in.team_id, current_user.id, required_roles=[RoleEnum.leader, RoleEnum.member]
    )
    
    schedule = Schedule(
        title=schedule_in.title,
        description=schedule_in.description,
        start_time=schedule_in.start_time,
        end_time=schedule_in.end_time,
        status=schedule_in.status,
        team_id=schedule_in.team_id,
        created_by=current_user.id
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

@router.get("/{schedule_id}", response_model=ScheduleResponse, summary="일정 단건 상세 조회", responses={**_401, **_403, **_404})
def get_schedule(
    schedule_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """일정 상세 조회 (소속 팀원만 접근 가능)"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
        
    deps.check_team_membership(db, schedule.team_id, current_user.id)
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleResponse, summary="일정 수정", responses={**_401, **_403, **_404})
def update_schedule(
    schedule_id: int,
    schedule_in: ScheduleUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """일정 상세 수정. 생성자 본인 또는 Team Leader만 가능"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
        
    membership = deps.check_team_membership(db, schedule.team_id, current_user.id)
    if schedule.created_by != current_user.id and membership.role != RoleEnum.leader:
         raise HTTPException(status_code=403, detail="일정 정보 변경은 이를 직접 생성한 사람 혹은 팀 리더만 수행할 수 있습니다.")
    
    if schedule_in.title is not None:
        schedule.title = schedule_in.title
    if schedule_in.description is not None:
        schedule.description = schedule_in.description
    if schedule_in.start_time is not None:
        schedule.start_time = schedule_in.start_time
    if schedule_in.end_time is not None:
        schedule.end_time = schedule_in.end_time
    if schedule_in.status is not None:
        schedule.status = schedule_in.status
        
    db.commit()
    db.refresh(schedule)
    return schedule

@router.patch("/{schedule_id}/status", response_model=ScheduleResponse, summary="일정 상태 변경 (퀵)", responses={**_401, **_403, **_404})
def update_schedule_status(
    schedule_id: int,
    status_in: ScheduleStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """상태값(PENDING 등)만 빠르게 변경 시 사용 (ex: 칸반 보드)"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
        
    deps.check_team_membership(db, schedule.team_id, current_user.id, required_roles=[RoleEnum.leader, RoleEnum.member])
    
    schedule.status = status_in.status
    db.commit()
    db.refresh(schedule)
    return schedule

@router.delete("/{schedule_id}", status_code=204, summary="일정 삭제", responses={**_401, **_403, **_404})
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """일정 완전 삭제. 생성자 본인 또는 Team Leader만 가능"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
        
    membership = deps.check_team_membership(db, schedule.team_id, current_user.id)
    if schedule.created_by != current_user.id and membership.role != RoleEnum.leader:
         raise HTTPException(status_code=403, detail="일정 삭제는 이를 직접 생성한 사람 혹은 팀 리더만 수행할 수 있습니다.")
         
    db.delete(schedule)
    db.commit()

# =======================================================
# 일정 할당 파트 (/schedules/{id}/assignees)
# =======================================================
@router.get("/{schedule_id}/assignees", response_model=List[ScheduleAssigneeResponse], summary="담당자 목록 조회", responses={**_401, **_403, **_404})
def get_assignees(
    schedule_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """일정에 배치된 담당자 목록 불러오기"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
    deps.check_team_membership(db, schedule.team_id, current_user.id)
    
    return db.query(ScheduleAssignee).filter(ScheduleAssignee.schedule_id == schedule_id).all()

@router.post("/{schedule_id}/assignees", status_code=201, summary="담당자 다중 배정", responses={**_401, **_403, **_404})
def add_assignees(
    schedule_id: int,
    assignees_in: ScheduleAssigneeCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """일정에 담당자들 다중 배정 (user_ids 리스트 기반)"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
        
    deps.check_team_membership(db, schedule.team_id, current_user.id, required_roles=[RoleEnum.leader, RoleEnum.member])
    
    for uid in assignees_in.user_ids:
        # 1. 해당 유저가 팀에 소속되어 있는지 검증 (가장 중요)
        tm = db.query(TeamMember).filter(TeamMember.team_id == schedule.team_id, TeamMember.user_id == uid).first()
        if not tm:
            raise HTTPException(status_code=400, detail=f"작업 배정 실패: 유저 {uid}는 이 팀의 소속 멤버가 아닙니다.")
            
        # 2. 이미 할당되어 있는지 체크 -> 없다면 신규 배정
        exists = db.query(ScheduleAssignee).filter(ScheduleAssignee.schedule_id == schedule_id, ScheduleAssignee.user_id == uid).first()
        if not exists:
            assignee = ScheduleAssignee(schedule_id=schedule_id, user_id=uid)
            db.add(assignee)
            
    db.commit()
    return {"detail": "담당자 배정 완료"}

@router.delete("/{schedule_id}/assignees/{user_id}", status_code=204, summary="담당자 제거", responses={**_401, **_403, **_404})
def remove_assignee(
    schedule_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """담당자 라인업에서 특정 유저 컷"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
        
    membership = deps.check_team_membership(db, schedule.team_id, current_user.id)
    
    # 팀원 본인이 스스로 나가는건 허용, 남을 쳐낼 땐 리더나 일정 생성자만 가능하도록 필터!
    if current_user.id != user_id and schedule.created_by != current_user.id and membership.role != RoleEnum.leader:
         raise HTTPException(status_code=403, detail="다른 회원의 작업 배정 해제는 팀 리더 혹은 일정 생성자만 가능합니다.")

    target = db.query(ScheduleAssignee).filter(ScheduleAssignee.schedule_id == schedule_id, ScheduleAssignee.user_id == user_id).first()
    if target:
        db.delete(target)
        db.commit()
