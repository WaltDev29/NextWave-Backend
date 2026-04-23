from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import get_password_hash
from app.db.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.logger import get_logger
from app.core.file_upload import save_upload_image, delete_image

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


@router.patch(
    "/me/image",
    response_model=UserResponse,
    summary="내 프로필 이미지 업로드",
    responses={**_401, 400: {"description": "허용되지 않는 파일 형식 또는 크기 초과"}}
)
async def upload_user_image(
    file: UploadFile = File(..., description="JPG, PNG, WEBP, GIF (최대 5MB)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    프로필 이미지를 업로드합니다. 기존 이미지가 있으면 자동으로 교체됩니다.
    업로드된 이미지는 `/static/uploads/users/{filename}` 경로로 서빙됩니다.
    """
    image_path = await save_upload_image(file, subdir="users", old_path=current_user.image_path)
    current_user.image_path = image_path
    db.commit()
    db.refresh(current_user)
    logger.info("[프로필 이미지 업로드] user_id=%s, path=%s", current_user.id, image_path)
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="내 정보 수정 (username / 비밀번호)",
    responses={**_401}
)
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    username 또는 비밀번호를 수정합니다. 전달된 필드만 업데이트됩니다.
    이미지 변경은 `PATCH /users/me/image` 를 사용하세요.
    """
    if user_in.username is not None:
        current_user.username = user_in.username
    if user_in.password is not None:
        from app.core.security import get_password_hash
        current_user.password_hash = get_password_hash(user_in.password)
    db.commit()
    db.refresh(current_user)
    logger.info("[유저 정보 수정] user_id=%s", current_user.id)
    return current_user


@router.delete(
    "/me",
    status_code=204,
    summary="회원 탈퇴",
    responses={**_401}
)
def delete_user_me(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    현재 로그인한 계정을 삭제합니다. 소속된 팀 멤버 정보가 삭제되며, 프로필 이미지 파일도 서버에서 제거됩니다.
    (팀의 리더인 경우 팀을 먼저 삭제하거나 리더를 위임해야 탈퇴할 수 있도록 하는 로직은 추후 확장 가능)
    """
    # 이미지 파일 삭제
    delete_image(current_user.image_path)

    db.delete(current_user)
    db.commit()
    logger.info("[회원 탈퇴 완료] user_id=%s, email=%s", current_user.id, current_user.email)
