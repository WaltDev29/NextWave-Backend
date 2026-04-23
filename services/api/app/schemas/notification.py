from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationCreate(BaseModel):
    schedule_id: int
    remind_at: datetime

class NotificationUpdate(BaseModel):
    remind_at: Optional[datetime] = None
    is_enabled: Optional[bool] = None

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    schedule_id: int
    remind_at: datetime
    is_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True
