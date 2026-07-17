from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Wilson Lab API"
    environment: str = "development"
    database_url: str = "sqlite:///./wilson_lab.db"
    jwt_secret: str = "replace-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    runtime_mode: str = "mock"
    cors_origins: list[str] = ["http://localhost:5173"]
    managed_label: str = "wilson-lab.managed=true"
    seed_demo_users: bool = True
    viewer_username: str = "viewer"
    viewer_password: str = "viewer-demo-change-me"
    admin_username: str = "admin"
    admin_password: str = "admin-demo-change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="WILSON_LAB_",
        extra="ignore",
    )

    @field_validator("runtime_mode")
    @classmethod
    def validate_runtime_mode(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"mock", "docker"}:
            raise ValueError("runtime_mode must be 'mock' or 'docker'")
        return normalized

    @field_validator("jwt_secret")
    @classmethod
    def reject_default_secret_in_production(cls, value: str, info):
        environment = str(info.data.get("environment", "development")).lower()
        if environment == "production" and value == "replace-this-in-production":
            raise ValueError("Set WILSON_LAB_JWT_SECRET in production")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
