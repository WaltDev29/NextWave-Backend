from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.core.config import settings
from app.db.database import get_db
from app.db.models import User, TeamMember, RoleEnum
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        # JWT 토큰 복호화
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="요청을 검증할 수 없습니다. (토큰 만료 혹은 올바르지 않은 값)",
        )
    # 복호화된 ID 기반으로 User 검증
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="인증된 회원을 찾을 수 없습니다.")
    return user


def check_team_membership(db: Session, team_id: int, user_id: int, required_roles: list[RoleEnum] = None) -> TeamMember:
    """
    팀 속 소속 및 권한 체크 유틸리티 (전역 사용)
    """
    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="팀에 접근할 수 있는 권한이 없습니다.")
    
    if required_roles and membership.role not in required_roles:
        raise HTTPException(status_code=403, detail="이 작업을 수행하기 위한 권한이 부족합니다.")
        
    return membership
