from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"
    allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    provider_timeout_seconds: float = Field(default=15, gt=0, le=30)
    extraction_deadline_seconds: float = Field(default=45, gt=0, le=60)
    max_output_tokens: int = Field(default=2500, ge=256, le=4000)
    rate_limit_per_minute: int = Field(default=5, ge=1, le=30)
    global_rate_limit_per_minute: int = Field(default=30, ge=1, le=100)
    max_concurrent_requests: int = Field(default=3, ge=1, le=5)
    input_cost_per_million: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    output_cost_per_million: float | None = Field(default=None, ge=0, allow_inf_nan=False)
