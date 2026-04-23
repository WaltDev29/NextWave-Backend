"""
구조화된 로깅 모듈
- uvicorn 로거를 확장하여 타임스탬프, 레벨, 메시지를 표준 출력
- 주요 분기점(인증 실패, 권한 오류, DB 에러 등)에서 호출
"""
import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    호출한 모듈 이름을 기준으로 구조화된 로거를 반환.
    uvicorn의 로그 포맷과 일관되도록 동일한 핸들러/포매터를 사용.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # 루트 로거 중복 출력 방지

    return logger
