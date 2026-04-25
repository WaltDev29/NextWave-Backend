from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.api import deps
from app.db.models import User
from app.schemas.token import Token
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["🔐 인증 (Auth)"])

_401 = {401: {"description": "이메일 또는 비밀번호가 올바르지 않음"}}

@router.post(
    "/login/access-token",
    response_model=Token,
    summary="로그인 및 JWT 토큰 발급",
    responses={**_401}
)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 호환 토큰 로그인 (이메일 주소를 **username** 필드에 전송)
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        logger.warning("[로그인 실패] email=%s", form_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 혹은 비밀번호가 틀렸습니다.")

    logger.info("[로그인 성공] user_id=%s, email=%s", user.id, user.email)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
