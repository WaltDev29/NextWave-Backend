from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import Notification, Schedule, User
from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["🔔 알림 (Notifications)"])

_401 = {401: {"description": "인증 토큰 없음 또는 만료"}}
_403 = {403: {"description": "자신의 알림만 접근 가능"}}
_404 = {404: {"description": "알림을 찾을 수 없음"}}


@router.post("/", response_model=NotificationResponse, summary="알림 등록", responses={**_401, **_403})
def create_notification(
    *,
    db: Session = Depends(deps.get_db),
    noti_in: NotificationCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """일정에 대한 알림 등록 (해당 일정 팀의 소속 멤버만 가능)"""
    schedule = db.query(Schedule).filter(Schedule.id == noti_in.schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")

    # 해당 일정이 소속된 팀의 멤버인지 확인
    deps.check_team_membership(db, schedule.team_id, current_user.id)

    # 이미 해당 일정에 본인 알림이 존재하는 경우 중복 생성 방지
    existing = db.query(Notification).filter(
        Notification.schedule_id == noti_in.schedule_id,
        Notification.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="해당 일정에 대한 알림이 이미 존재합니다. 기존 알림을 수정해주세요.")

    noti = Notification(
        user_id=current_user.id,
        schedule_id=noti_in.schedule_id,
        remind_at=noti_in.remind_at,
    )
    db.add(noti)
    db.commit()
    db.refresh(noti)
    return noti


@router.get("/me", response_model=List[NotificationResponse], summary="내 알림 목록 조회", responses={**_401})
def get_my_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """내 알림 목록 전체 조회 (알림 시간 오름차순)"""
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.remind_at.asc())
        .all()
    )


@router.put("/{notification_id}", response_model=NotificationResponse, summary="알림 수정 (시간/활성 여부)", responses={**_401, **_404})
def update_notification(
    notification_id: int,
    noti_in: NotificationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """알림 수정 (알림 시간 변경 또는 활성/비활성 토글). 본인 알림만 수정 가능"""
    noti = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id  # 본인 소유 확인
    ).first()
    if not noti:
        raise HTTPException(status_code=404, detail="해당 알림을 찾을 수 없거나 접근 권한이 없습니다.")

    if noti_in.remind_at is not None:
        noti.remind_at = noti_in.remind_at
    if noti_in.is_enabled is not None:
        noti.is_enabled = noti_in.is_enabled

    db.commit()
    db.refresh(noti)
    return noti


@router.delete("/{notification_id}", status_code=204, summary="알림 삭제", responses={**_401, **_404})
def delete_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """알림 삭제. 본인 알림만 삭제 가능"""
    noti = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not noti:
        raise HTTPException(status_code=404, detail="해당 알림을 찾을 수 없거나 접근 권한이 없습니다.")

    db.delete(noti)
    db.commit()
