from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import get_password_hash
from app.db.models import User
from app.schemas.user import UserCreate, UserResponse
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["👤 유저 (Users)"])

_400 = {400: {"description": "이메일 중복 등 잘못된 요청"}}
_401 = {401: {"description": "인증 토큰이 없거나 유효하지 않음"}}

@router.post(
    "/signup",
    response_model=UserResponse,
    summary="회원가입",
    responses={**_400}
)
def create_user(*, db: Session = Depends(deps.get_db), user_in: UserCreate):
    """
    신규 회원 가입. 이메일 중복 시 **400** 에러 반환.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="해당 이메일로 가입한 회원이 이미 존재합니다.")

    user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("[회원가입 완료] user_id=%s, email=%s", user.id, user.email)
    return user

@router.get(
    "/me",
    response_model=UserResponse,
    summary="내 정보 조회",
    responses={**_401}
)
def read_user_me(current_user: User = Depends(deps.get_current_user)):
    """
    JWT 토큰으로 인증된 현재 사용자 정보를 반환합니다.
    """
    return current_user
