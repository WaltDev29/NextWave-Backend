from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    """팀 정보 수정. image_path는 PATCH /{team_id}/image 로 따로 처리합니다."""
    name: Optional[str] = None
    description: Optional[str] = None

class TeamResponse(TeamBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==== TeamMember 스키마 ====
class TeamMemberCreate(BaseModel):
    email: EmailStr
    role: str = "member"

class TeamMemberResponse(BaseModel):
    id: int = Field(..., description="멤버십 레코드 ID")
    user_id: int = Field(..., description="사용자 고유 ID", example=5)
    team_name: str = Field(..., description="소속 팀 이름", example="개발팀")
    user_name: str = Field(..., description="사용자 이름", example="홍길동")
    role: str = Field(..., description="팀 내 역할 (leader, member, guest)", example="member")

    class Config:
        from_attributes = True