from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" )

    # ── AWS / S3 ──────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID:     str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION:            str = "ap-northeast-2"
    S3_BUCKET:             str          # 영상 저장 버킷 이름

    # ── Whisper STT ───────────────────────────────────────────────
    WHISPER_DEVICE:       str = "cuda"  # "cpu" | "cuda"
    WHISPER_COMPUTE_TYPE: str = "int8"  # "int8" | "float16" | "float32"

    # ── Claude (LLM 교정) ─────────────────────────────────────────
    ANTHROPIC_API_KEY:  str
    CLAUDE_HAIKU_MODEL: str   = "claude-haiku-4-5-20251001"
    LLM_TIMEOUT_SECONDS: float = 15.0

    # ── Consul (점수 정책) ────────────────────────────────────────
    CONSUL_URL:   str = "http://consul:8500"
    CONSUL_TOKEN: str = ""               # ACL 미사용 시 빈 문자열

    # ── Spring Boot 웹훅 ──────────────────────────────────────────
    SPRING_WEBHOOK_URL: str
    FEEDBACK_SPRING_WEBHOOK_URL: str
    
    OPENAI_API_KEY:  str

settings = Settings()