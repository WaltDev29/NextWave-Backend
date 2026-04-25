from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일 주소", example="user@example.com")
    username: str = Field(..., description="사용자 이름", example="홍길동")
    job: Optional[str] = Field(None, description="직업 (직장인, 학생, 주부 등)", example="직장인")
    age: int = Field(..., description="나이 (세)", example=25)
    gender: Optional[str] = Field(None, description="성별 (남, 여, 무관)", example="남")
    image_path: Optional[str] = Field(None, description="프로필 이미지 경로")

# 생성 프로퍼티 (회원가입 시에만 사용 목적을 받음)
class UserCreate(UserBase):
    password: str = Field(..., description="비밀번호")
    purpose: Optional[str] = Field(None, description="서비스 사용 목적 (DB 저장 안함)", example="업무 및 일정 관리")

# 일반 정보 업데이트 (이미지는 PATCH /me/image 로 따로 처리)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="수정할 사용자 이름", example="김철수")
    password: Optional[str] = Field(None, description="수정할 비밀번호", example="newsecret123!")
    job: Optional[str] = Field(None, description="수정할 직업", example="학생")
    age: Optional[int] = Field(None, description="수정할 나이", example=22)
    gender: Optional[str] = Field(None, description="수정할 성별", example="여")

# 응답 모델 (비밀번호 제외)
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
