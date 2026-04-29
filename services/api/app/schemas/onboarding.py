from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class OnboardingSchedule(BaseModel):
    title: str = Field(..., description="예시 일정 제목", example="프로젝트 팀 미팅")
    description: str = Field(..., description="예시 일정 상세 설명", example="현재 진행 상황을 공유하고 마일스톤을 점검하는 회의입니다.")
    start_time: str = Field(..., description="예시 일정 시작 시간 (ISO 포맷)", example="2026-04-26T14:00")
    end_time: str = Field(..., description="예시 일정 종료 시간 (ISO 포맷)", example="2026-04-26T15:00")

class OnboardingMemo(BaseModel):
    title: str = Field(..., description="예시 메모 제목", example="아이디어 브레인스토밍")
    content: str = Field(..., description="예시 메모 상세 내용", example="새로운 피드백 위젯 디자인에 대한 여러 아이디어를 기록합니다.")

class OnboardingGuideContent(BaseModel):
    primary_feature: str = Field(..., description="사용자가 가장 먼저/많이 사용할 것으로 예상되는 기능 (team_manage, schedule, memo 중 하나)", example="schedule")
    example_schedule: OnboardingSchedule
    example_memo: OnboardingMemo

class OnboardingResponse(BaseModel):
    user_name: str = Field(..., description="사용자 이름", example="홍길동")
    guide: OnboardingGuideContent

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
