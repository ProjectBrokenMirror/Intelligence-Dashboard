from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://pv:pv@localhost:5432/pv_intel"
    sources_config_path: str = "config/sources.yaml"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    ingest_interval_minutes: int = 30
    # Puerto Vallarta approximate center
    weather_latitude: float = 20.6534
    weather_longitude: float = -105.2253


settings = Settings()
