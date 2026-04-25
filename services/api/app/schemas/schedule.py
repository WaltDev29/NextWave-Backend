from pydantic import BaseModel, model_validator, Field
from datetime import datetime
from typing import Optional, List

# ==== Schedule 스키마 ====
class ScheduleBase(BaseModel):
    title: str = Field(..., description="일정 제목", example="주간 회의")
    description: Optional[str] = Field(None, description="상세 설명", example="프로젝트 진행 상황 공유")
    start_time: datetime = Field(..., description="시작 시간")
    end_time: Optional[datetime] = Field(None, description="종료 시간")
    status: str = Field("PENDING", description="상태 (PENDING, IN_PROGRESS, COMPLETED)", example="PENDING")
    team_id: int = Field(..., description="소속 팀 ID")

class ScheduleCreate(ScheduleBase):
    assignees: Optional[List[int]] = Field(default=[], description="담당자로 지정할 유저 ID 리스트", example=[1, 2])

    @model_validator(mode='after')
    def check_start_end_time(self) -> 'ScheduleCreate':
        if self.end_time and self.start_time > self.end_time:
            raise ValueError("종료 시간(end_time)은 시작 시간(start_time)보다 과거일 수 없습니다.")
        return self

class ScheduleUpdate(BaseModel):
    title: Optional[str] = Field(None, description="수정할 제목")
    description: Optional[str] = Field(None, description="수정할 상세 설명")
    start_time: Optional[datetime] = Field(None, description="수정할 시작 시간")
    end_time: Optional[datetime] = Field(None, description="수정할 종료 시간")
    status: Optional[str] = Field(None, description="수정할 상태")
    assignees: Optional[List[int]] = Field(None, description="변경할 담당자 ID 리스트 (제공 시 기존 목록 교체)")

class ScheduleStatusUpdate(BaseModel):
    status: str

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


# ==== ScheduleResponse 스키마 ====
class ScheduleResponse(ScheduleBase):
    id: int
    created_by: int
    assignees: List[ScheduleAssigneeResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
