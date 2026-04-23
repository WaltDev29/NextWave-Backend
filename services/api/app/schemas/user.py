from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str
    image_path: Optional[str] = None

# 생성 프로퍼티
class UserCreate(UserBase):
    password: str

# 일반 정보 업데이트 (이미지는 PATCH /me/image 로 따로 처리)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

# 응답 모델 (비밀번호 제외)
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
