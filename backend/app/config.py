from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://manutencar:change-me@localhost:3306/manutencar"
    jwt_secret: str = "change-me-in-production"
    jwt_expires_minutes: int = 60
    auth_private_key_path: str = "./secrets/auth-private-key.pem"
    frontend_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
