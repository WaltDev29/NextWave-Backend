from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models import NotificationType

# 1. 앱 통합 알림 (Inbox) 스키마
class AppNotificationBase(BaseModel):
    title: str
    content: str
    type: NotificationType
    related_id: Optional[int] = None

class AppNotificationResponse(AppNotificationBase):
    id: int
    receiver_id: int
    sender_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    sender_name: Optional[str] = None

    class Config:
        from_attributes = True

# 2. 기존 일정 리마인더용 스키마 (필요시 유지/복구)
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
