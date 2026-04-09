from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://pv:pv@localhost:5432/pv_intel"
    sources_config_path: str = "config/sources.yaml"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    ingest_interval_minutes: int = 30
    enrichment_interval_minutes: int = 60
    enrichment_batch_size: int = 5
    # Ollama: e.g. http://ollama:11434 or http://host.docker.internal:11434
    ollama_base_url: str | None = None
    ollama_model: str = "llama3.2"
    # Groq OpenAI-compatible API (optional)
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    # Puerto Vallarta approximate center
    weather_latitude: float = 20.6534
    weather_longitude: float = -105.2253

    @field_validator("ollama_base_url", "groq_api_key", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: object) -> object:
        if v == "":
            return None
        return v


settings = Settings()
