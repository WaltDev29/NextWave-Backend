from pydantic import BaseModel, EmailStr
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
    id: int
    user_id: int
    team_name: str
    user_name: str
    role: str

    class Config:
        from_attributes = True