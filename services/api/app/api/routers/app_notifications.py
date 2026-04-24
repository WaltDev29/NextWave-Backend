from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import AppNotification, User, TeamMember, Team, RoleEnum, NotificationType
from app.schemas.notification import AppNotificationResponse

router = APIRouter(prefix="/inbox", tags=["🔔 알림함 (Inbox)"])

_401 = {401: {"description": "인증 토큰 없음 또는 만료"}}
_404 = {404: {"description": "알림 정보를 찾을 수 없음"}}

@router.get("/", response_model=List[AppNotificationResponse], summary="내 알림 목록 조회", responses={**_401})
def get_my_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """최신순으로 사용자의 알림 목록을 가져옵니다."""
    notifications = (
        db.query(AppNotification)
        .filter(AppNotification.receiver_id == current_user.id)
        .order_by(AppNotification.created_at.desc())
        .limit(50)
        .all()
    )
    
    # 보낸 사람 이름 매핑 (Optional)
    for n in notifications:
        if n.sender:
            n.sender_name = n.sender.username
            
    return notifications

@router.patch("/{notification_id}/read", response_model=AppNotificationResponse, summary="알림 읽음 처리", responses={**_401, **_404})
def mark_as_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """특정 알림을 읽음 상태로 변경합니다."""
    noti = db.query(AppNotification).filter(
        AppNotification.id == notification_id, 
        AppNotification.receiver_id == current_user.id
    ).first()
    
    if not noti:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다.")
        
    noti.is_read = True
    db.commit()
    db.refresh(noti)
    return noti

@router.post("/{notification_id}/accept", summary="팀 초대 수락", responses={**_401, **_404})
def accept_team_invite(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    팀 초대를 수락하여 실제 팀 멤버로 정식 가입합니다.
    - 성공 시: 초대자가 보낸 [ROLE:...] 정보를 파싱하여 해당 권한으로 `TeamMember` 테이블에 등록됩니다.
    - 이후: 초대자에게 수락 알림(`INVITE_ACCEPTED`)이 전송됩니다.
    """
    noti = db.query(AppNotification).filter(
        AppNotification.id == notification_id, 
        AppNotification.receiver_id == current_user.id,
        AppNotification.type == NotificationType.TEAM_INVITE
    ).first()
    
    if not noti or not noti.related_id:
        raise HTTPException(status_code=404, detail="유효한 초대 알림이 아닙니다.")

    team_id = noti.related_id
    
    # 1. 이미 멤버인지 확인
    existing = db.query(TeamMember).filter(
        TeamMember.team_id == team_id, 
        TeamMember.user_id == current_user.id
    ).first()
    
    if not existing:
        # 2. 역할(Role) 파싱 로직 추가
        role = RoleEnum.member
        if "[ROLE:" in noti.content:
            try:
                role_str = noti.content.split("[ROLE:")[1].split("]")[0]
                role = RoleEnum(role_str)
            except (IndexError, ValueError):
                role = RoleEnum.member

        # 3. 팀 멤버 추가
        new_member = TeamMember(team_id=team_id, user_id=current_user.id, role=role)
        db.add(new_member)
        
        # 4. 초대자에게 수락 알림 전송 (Optional)
        if noti.sender_id:
            accept_noti = AppNotification(
                receiver_id=noti.sender_id,
                sender_id=current_user.id,
                type=NotificationType.INVITE_ACCEPTED,
                title="팀 초대 수락",
                content=f"{current_user.username}님이 팀 초대를 수락했습니다.",
                related_id=team_id
            )
            db.add(accept_noti)

    # 5. 초대 알림 읽음 처리 및 삭제 혹은 상태 업데이트
    noti.is_read = True
    db.commit()
    return {"message": "팀 초대를 수락했습니다."}

@router.post("/{notification_id}/reject", summary="팀 초대 거절", responses={**_401, **_404})
def reject_team_invite(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """팀 초대를 거절합니다."""
    noti = db.query(AppNotification).filter(
        AppNotification.id == notification_id, 
        AppNotification.receiver_id == current_user.id,
        AppNotification.type == NotificationType.TEAM_INVITE
    ).first()
    
    if not noti:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다.")

    # 1. 초대자에게 거절 알림 전송
    if noti.sender_id:
        reject_noti = AppNotification(
            receiver_id=noti.sender_id,
            sender_id=current_user.id,
            type=NotificationType.INVITE_REJECTED,
            title="팀 초대 거절",
            content=f"{current_user.username}님이 팀 초대를 거절했습니다.",
            related_id=noti.related_id
        )
        db.add(reject_noti)

    # 2. 초대 알림 읽음 처리
    noti.is_read = True
    db.commit()
    return {"message": "팀 초대를 거절했습니다."}
