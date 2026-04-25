import math
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import Memo, MemoMention, Comment, User, RoleEnum, AppNotification, NotificationType
from app.schemas.memo import (
    MemoCreate, MemoUpdate, MemoResponse, MemoDetailResponse,
    CommentCreate, CommentResponse,
)

router = APIRouter(prefix="/memos", tags=["📝 메모 (Memos)"])
team_memos_router = APIRouter(prefix="/teams", tags=["📝 메모 (Memos)"])
schedule_memos_router = APIRouter(prefix="/schedules", tags=["📝 메모 (Memos)"])

_401 = {401: {"description": "인증 토큰 없음 또는 만료"}}
_403 = {403: {"description": "팀 소속이 아니거나 권한 부족"}}
_404 = {404: {"description": "메모 또는 댓글을 찾을 수 없음"}}


# =======================================================
# 팀/일정 하위 라우터 파트
# =======================================================
@team_memos_router.get("/{team_id}/memos", response_model=List[MemoResponse], summary="팀 메모 목록 조회", responses={**_401, **_403})
def get_team_memos(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """팀의 전체 메모 목록 (최신순)"""
    deps.check_team_membership(db, team_id, current_user.id)
    return db.query(Memo).filter(Memo.team_id == team_id).order_by(Memo.created_at.desc()).all()


@schedule_memos_router.get("/{schedule_id}/memos", response_model=List[MemoResponse], summary="일정 종속 메모 목록", responses={**_401, **_403})
def get_schedule_memos(
    schedule_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """특정 일정에 달린 메모 목록"""
    memos = db.query(Memo).filter(Memo.schedule_id == schedule_id).order_by(Memo.created_at.desc()).all()
    if memos:
        deps.check_team_membership(db, memos[0].team_id, current_user.id)
    return memos


# =======================================================
# 메모 CRUD 파트
# =======================================================
@router.post("/", response_model=MemoDetailResponse, summary="메모 작성", responses={**_401, **_403})
def create_memo(
    *,
    db: Session = Depends(deps.get_db),
    memo_in: MemoCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    새 메모를 작성합니다.
    - **멘션**: `mentions` 필드에 유저 ID 목록을 보내면 해당 유저들에게 **멘션 알림**이 전송됩니다.
    """
    deps.check_team_membership(db, memo_in.team_id, current_user.id, required_roles=[RoleEnum.leader, RoleEnum.member])

    memo = Memo(
        title=memo_in.title,
        content=memo_in.content,
        author_id=current_user.id,
        team_id=memo_in.team_id,
        schedule_id=memo_in.schedule_id,
    )
    db.add(memo)
    db.flush()  # id 확보를 위해 flush (commit 전)

    # 멘션 대상자 일괄 삽입 및 알림 생성
    for uid in (memo_in.mentions or []):
        db.add(MemoMention(memo_id=memo.id, user_id=uid))
        
        # 중복 방지를 위해 본인 제외
        if uid != current_user.id:
            noti = AppNotification(
                receiver_id=uid,
                sender_id=current_user.id,
                type=NotificationType.MEMO_MENTION,
                title="메모 멘션",
                content=f"'{memo.title}' 메모에서 당신을 언급했습니다.",
                related_id=memo.id
            )
            db.add(noti)

    db.commit()
    db.refresh(memo)
    return memo


@router.get("/{memo_id}", response_model=MemoDetailResponse, summary="메모 상세 조회 (멘션+댓글 포함)", responses={**_401, **_403, **_404})
def get_memo(
    memo_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """메모 단건 상세 조회 (멘션 유저 및 댓글 목록 포함)"""
    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")
    deps.check_team_membership(db, memo.team_id, current_user.id)
    return memo


@router.put("/{memo_id}", response_model=MemoDetailResponse, summary="메모 수정", responses={**_401, **_403, **_404})
def update_memo(
    memo_id: int,
    memo_in: MemoUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """메모 수정 (작성자 본인만 가능). 멘션 목록이 주어지면 기존 멘션을 전부 교체"""
    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")
    if memo.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="메모는 작성자 본인만 수정할 수 있습니다.")

    if memo_in.title is not None:
        memo.title = memo_in.title
    if memo_in.content is not None:
        memo.content = memo_in.content
    if memo_in.schedule_id is not None:
        memo.schedule_id = memo_in.schedule_id

    # 멘션 교체 및 신규 멘션자 알림
    if memo_in.mentions is not None:
        # 기존 멘션된 유저 정보 (알림 중복 방지용)
        existing_mentions = {m.user_id for m in db.query(MemoMention).filter(MemoMention.memo_id == memo.id).all()}
        
        db.query(MemoMention).filter(MemoMention.memo_id == memo.id).delete()
        for uid in memo_in.mentions:
            db.add(MemoMention(memo_id=memo.id, user_id=uid))
            
            # 새로 멘션된 사람에게만(작성자 제외) 알림 발송
            if uid not in existing_mentions and uid != current_user.id:
                db.add(AppNotification(
                    receiver_id=uid,
                    sender_id=current_user.id,
                    type=NotificationType.MEMO_MENTION,
                    title="메모 멘션",
                    content=f"'{memo.title}' 메모에서 당신을 언급했습니다.",
                    related_id=memo.id
                ))

    db.commit()
    db.refresh(memo)
    return memo


@router.delete("/{memo_id}", status_code=204, summary="메모 삭제", responses={**_401, **_403, **_404})
def delete_memo(
    memo_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """메모 삭제 (작성자 또는 팀 리더만 가능)"""
    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")

    membership = deps.check_team_membership(db, memo.team_id, current_user.id)
    if memo.author_id != current_user.id and membership.role != RoleEnum.leader:
        raise HTTPException(status_code=403, detail="메모 삭제는 작성자 혹은 팀 리더만 가능합니다.")

    db.delete(memo)
    db.commit()


# =======================================================
# 댓글 CRUD 파트
# =======================================================
@router.post("/{memo_id}/comments", response_model=CommentResponse, summary="댓글 작성", responses={**_401, **_403, **_404})
def create_comment(
    memo_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    특정 메모에 댓글을 작성합니다.
    - **알림**: 본인 글이 아닌 경우, 메모 작성자에게 **신규 댓글 알림**이 전송됩니다.
    """
    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")
    deps.check_team_membership(db, memo.team_id, current_user.id, required_roles=[RoleEnum.leader, RoleEnum.member])

    comment = Comment(
        memo_id=memo_id,
        author_id=current_user.id,
        content=comment_in.content,
    )
    db.add(comment)
    
    # 메모 작성자에게 알림 전송 (본인이 쓴 글이 아닐 때만)
    if memo.author_id != current_user.id:
        noti = AppNotification(
            receiver_id=memo.author_id,
            sender_id=current_user.id,
            type=NotificationType.COMMENT,
            title="새 댓글 알림",
            content=f"귀하의 메모 '{memo.title}'에 새로운 댓글이 달렸습니다.",
            related_id=memo.id
        )
        db.add(noti)

    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{memo_id}/comments", response_model=List[CommentResponse], summary="댓글 목록 조회", responses={**_401, **_403, **_404})
def get_comments(
    memo_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """메모의 전체 댓글 목록 조회 (오래된 순)"""
    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")
    deps.check_team_membership(db, memo.team_id, current_user.id)

    return db.query(Comment).filter(Comment.memo_id == memo_id).order_by(Comment.created_at.asc()).all()


@router.delete("/{memo_id}/comments/{comment_id}", status_code=204, summary="댓글 삭제", responses={**_401, **_403, **_404})
def delete_comment(
    memo_id: int,
    comment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """댓글 삭제 (작성자 혹은 팀 리더만 가능)"""
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.memo_id == memo_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    membership = deps.check_team_membership(db, memo.team_id, current_user.id)
    if comment.author_id != current_user.id and membership.role != RoleEnum.leader:
        raise HTTPException(status_code=403, detail="댓글 삭제는 작성자 혹은 팀 리더만 가능합니다.")

    db.delete(comment)
    db.commit()
