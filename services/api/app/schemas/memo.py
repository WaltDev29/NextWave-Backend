from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ==== Mention 스키마 ====
class MemoMentionResponse(BaseModel):
    id: int
    user_id: int
    user_name: str

    class Config:
        from_attributes = True


# ==== Comment 스키마 ====
class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    memo_id: int
    author_id: int
    author_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==== Memo 스키마 ====
class MemoCreate(BaseModel):
    title: str
    content: Optional[str] = None
    team_id: int
    schedule_id: Optional[int] = None
    mentions: Optional[List[int]] = []  # 멘션할 유저 ID 리스트

class MemoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    schedule_id: Optional[int] = None
    mentions: Optional[List[int]] = None  # 제공되면 전체 교체(replace)

class MemoResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    author_id: int
    author_name: str
    team_id: int
    schedule_id: Optional[int] = None
    schedule_title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MemoDetailResponse(MemoResponse):
    """상세 조회 시 멘션 & 댓글도 함께 반환"""
    mentions: List[MemoMentionResponse] = []
    comments: List[CommentResponse] = []

    class Config:
        from_attributes = True

