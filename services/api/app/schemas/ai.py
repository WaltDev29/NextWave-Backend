from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# --- Contextual Example Schemas ---

class ContextualExampleRequest(BaseModel):
    part: Optional[Literal["memo", "schedule"]] = Field(None, description="클라이언트가 요청하는 컨텐츠 타입 (null일 경우 전부 요청)")
    team_id: int = Field(..., description="클라이언트가 요청하는 컨텐츠를 작성할 현재 팀")

class ExampleSchedule(BaseModel):
    title: str = Field(..., description="일정 제목")
    description: str = Field(..., description="일정 설명")
    start_time: str = Field(..., description="시작 시간 (%Y-%m-%d %H:%M)")
    end_time: str = Field(..., description="종료 시간 (%Y-%m-%d %H:%M)")
    assignee_ids: List[int] = Field(..., description="해당 일정의 담당자로 설정할 사용자 id(db pk)")

class ExampleMemo(BaseModel):
    title: str = Field(..., description="메모 제목")
    content: str = Field(..., description="메모 내용")
    mention_ids: List[int] = Field(..., description="메모에 멘션할 사용자 id(db pk)")
    schedule_id: Optional[int] = Field(None, description="어떤 일정과 연관된 메모인지 명시")

class ContextualExampleResponse(BaseModel):
    type: Literal["memo", "schedule", "all"] = Field(..., description="반환 컨텐츠 타입")
    rationale: str = Field(..., description="해당 컨텐츠를 생성한 이유")
    example_schedule: Optional[ExampleSchedule] = Field(None, description="예시 일정 데이터")
    example_memo: Optional[ExampleMemo] = Field(None, description="예시 메모 데이터")
