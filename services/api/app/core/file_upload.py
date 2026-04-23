"""
이미지 파일 저장 유틸리티
- 허용 확장자 및 크기를 검증한 뒤 UUID 기반 파일명으로 저장
- 기존 파일이 있을 경우 교체 전 자동 삭제
"""
import uuid
import os
from pathlib import Path
from fastapi import HTTPException, UploadFile

UPLOAD_ROOT = Path("/app/static/uploads")
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


def _extension_from_content_type(content_type: str) -> str:
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }.get(content_type, ".jpg")


async def save_upload_image(file: UploadFile, subdir: str, old_path: str | None = None) -> str:
    """
    이미지를 검증 후 저장하고 저장된 상대 경로를 반환한다.

    :param file: FastAPI UploadFile 객체
    :param subdir: 저장 서브디렉토리 (예: "users", "teams")
    :param old_path: 교체 시 삭제할 기존 파일 경로 ("/app/static/uploads/..." 절대경로)
    :return: DB에 저장할 상대 경로 문자열 (예: "/static/uploads/users/abc.jpg")
    """
    # 1. 파일 타입 검증
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 파일 형식입니다. ({', '.join(ALLOWED_CONTENT_TYPES)})"
        )

    # 2. 파일 읽기 + 크기 검증
    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="파일 크기는 5MB를 초과할 수 없습니다.")

    # 3. 저장 디렉토리 생성
    save_dir = UPLOAD_ROOT / subdir
    save_dir.mkdir(parents=True, exist_ok=True)

    # 4. UUID 기반 파일명으로 저장
    ext = _extension_from_content_type(file.content_type)
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = save_dir / filename

    with open(save_path, "wb") as f:
        f.write(contents)

    # 5. 기존 파일 삭제 (교체 시)
    if old_path:
        # old_path는 "/static/uploads/users/abc.jpg" 형태 → 절대경로로 변환
        old_abs = Path("/app") / old_path.lstrip("/")
        if old_abs.exists():
            os.remove(old_abs)

    # DB에 저장할 URL 경로 반환
    return f"/static/uploads/{subdir}/{filename}"
