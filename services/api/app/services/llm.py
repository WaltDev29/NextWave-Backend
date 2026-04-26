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

    def generate_onboarding_data(self, user_profile: dict) -> dict:
        """
        사용자 정보를 기반으로 예시 일정과 예시 메모를 생성합니다.
        """
        prompt = f"""
NextWave 프로젝트 협업 플랫폼의 온보딩 가이드를 위한 예시 데이터를 생성해줘.
사용자의 정보는 다음과 같아:
- 직업: {user_profile.get('job')}
- 나이: {user_profile.get('age')}
- 성별: {user_profile.get('gender')}
- 서비스 사용 목적: {user_profile.get('purpose')}

위 정보를 바탕으로 이 사용자가 서비스에 처음 들어왔을 때 흥미를 느낄만한 
1개의 예시 일정(제목, 내용)과 1개의 예시 메모(제목, 내용)를 작성해줘.

형식은 반드시 아래 JSON 구조를 지켜줘:
{{
    "example_schedule": {{
        "title": "일정 제목",
        "description": "일정 상세 내용"
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
                    {"role": "system", "content": "너는 협업 플랫폼 온보딩을 돕는 친절한 AI 비서야. 반드시 JSON 형식으로만 응답해."},
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
                "example_schedule": {
                    "title": "새 일정",
                    "description": "일정을 등록하여 체계적으로 관리할 수 있습니다!"
                },
                "example_memo": {
                    "title": "새 메모",
                    "content": "메모를 통해 아이디어를 기록하고 팀원들과 공유해보세요!"
                }
            }

llm_service = LLMService()
