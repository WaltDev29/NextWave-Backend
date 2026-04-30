from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NextWave"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    SECRET_KEY: str = "nextwave_super_secret_key_v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 1일
    ALGORITHM: str = "HS256"
    
    # LLM Settings
    LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    LLM_BASE_URL: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
