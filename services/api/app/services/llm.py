from openai import OpenAI
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # LLM_BASE_URL이 있으면 외부 모델, 없으면 OpenAI 기본 사용
        if settings.LLM_BASE_URL:
            self.client = OpenAI(
                api_key="APIKEY",
                base_url=settings.LLM_BASE_URL,
                default_headers={"User-Agent": "Mozilla/5.0"},
            )
            logger.info(f"Using external LLM: {settings.LLM_BASE_URL}")
        else:
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY
            )
            logger.info("Using OpenAI service")

    def generate_onboarding_data(self, user_profile: dict, current_time: str) -> dict:
        """
        사용자 정보를 기반으로 예시 일정과 예시 메모를 생성하고,
        가장 먼저 학습해야 할 핵심 기능을 추천합니다.
        """
        prompt = f"""
NextWave 프로젝트 협업 플랫폼의 온보딩 가이드를 위한 예시 데이터를 생성해줘.
사용자의 정보는 다음과 같아:
- 직업: {user_profile.get('job')}
- 나이: {user_profile.get('age')}
- 성별: {user_profile.get('gender')}
- 서비스 사용 목적: {user_profile.get('purpose')}
- 현재 일시: {current_time}

위 정보를 바탕으로 이 사용자가 서비스에 처음 들어왔을 때 가장 먼저 혹은 가장 많이 사용할 것이라 예상되는 기능을 하나 선택하고, 흥미를 느낄만한 1개의 예시 일정(제목, 내용)과 1개의 예시 메모(제목, 내용)를 작성해줘.

**일정 생성 가이드:**
- `start_time`과 `end_time`은 제공된 **현재 일시({current_time})**를 기준으로 오늘 혹은 가까운 미래의 실제 가능한 시간대로 설정해줘.
- 형식은 반드시 `YYYY-MM-DDTHH:MM`을 지켜야 해.

**핵심 기능 선택 로직 (primary_feature):**
- 다음 세 가지 기능 중 하나를 반드시 선택해야 함:
    1. `team_manage`: 협업, 팀 관리, 권한 설정 등이 주 목적인 경우
    2. `schedule`: 일정 관리, 미팅, 마일스톤 체크 등이 주 목적인 경우
    3. `memo`: 개인적인 기록, 아이디어 정리, 단순 문서화 등이 주 목적인 경우
- 사용자의 직업과 서비스 사용 목적을 분석하여 가장 적합한 것을 선택해.

**주의사항:** 
- 사용자에게 무언가를 하라고 제안하거나 추천하는 말투(예: ~해보세요, ~는 어떠신가요?)는 절대 사용하지 마.
- 일정의 상세 내용(`description`)과 메모의 내용(`content`)은 **최소 2줄(두 문장) 이상**의 구체적인 정보를 담아줘.
- 사용자 혼자 일정과 메모를 관리할 것이라 판단되는 경우 내용은 음슴체로 작성해.

형식은 반드시 아래 JSON 구조를 지켜줘:
{{
    "primary_feature": "team_manage | schedule | memo",
    "example_schedule": {{
        "title": "일정 제목",
        "description": "일정 상세 내용",
        "start_time": "YYYY-MM-DDTHH:MM",
        "end_time": "YYYY-MM-DDTHH:MM"
    }},
    "example_memo": {{
        "title": "메모 제목",
        "content": "메모 상세 내용"
    }}
}}
결과값은 오직 JSON만 반환해줘.
"""

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "너는 협업 플랫폼 온보딩을 위해 사용자가 직접 작성한 듯한 예시 데이터를 생성하고 핵심 기능을 추천하는 정밀한 AI야. 제안하는 말투를 지양하고 JSON 형식으로만 응답해."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"LLM 연동 중 오류 발생: {e}")
            # 오류 발생 시 기본값 반환
            return {
                "primary_feature": "schedule",
                "example_schedule": {
                    "title": "새 일정",
                    "description": "일정을 등록하여 체계적으로 관리할 수 있습니다!",
                    "start_time": current_time,
                    "end_time": current_time
                },
                "example_memo": {
                    "title": "새 메모",
                    "content": "메모를 통해 아이디어를 기록하고 팀원들과 공유해보세요!"
                }
            }

llm_service = LLMService()
