from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import Optional, List

# ==== Schedule 스키마 ====
class ScheduleBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "PENDING"
    team_id: int

class ScheduleCreate(ScheduleBase):
    @model_validator(mode='after')
    def check_start_end_time(self) -> 'ScheduleCreate':
        if self.end_time and self.start_time > self.end_time:
            raise ValueError("종료 시간(end_time)은 시작 시간(start_time)보다 과거일 수 없습니다.")
        return self

class ScheduleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None

class ScheduleStatusUpdate(BaseModel):
    status: str

class ScheduleResponse(ScheduleBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==== ScheduleAssignee 스키마 ====
class ScheduleAssigneeCreate(BaseModel):
    user_ids: List[int] # 다중 배정

class ScheduleAssigneeResponse(BaseModel):
    id: int
    schedule_id: int
    user_id: int
    user_name: str

    class Config:
        from_attributes = True
