from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# 공통 프로퍼티
class UserBase(BaseModel):
    email: EmailStr
    username: str

# 생성 프로퍼티
class UserCreate(UserBase):
    password: str

# 비밀번호 변경 등 업데이트 
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

# 응답 모델 (비밀번호 제외)
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
