from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_path: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==== TeamMember 스키마 ====
class TeamMemberCreate(BaseModel):
    email: EmailStr
    role: str = "member"

class TeamMemberResponse(BaseModel):
    id: int
    team_name: str
    user_name: str
    role: str

    class Config:
        from_attributes = True
