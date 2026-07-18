from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_JWT_SECRET = "replace-this-in-production"
DEFAULT_VIEWER_PASSWORD = "viewer-demo-change-me"
DEFAULT_ADMIN_PASSWORD = "admin-demo-change-me"


class Settings(BaseSettings):
    app_name: str = "Wilson Lab API"
    environment: str = "development"
    database_url: str = "sqlite:///./wilson_lab.db"
    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_secret_file: str | None = None
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    runtime_mode: str = "mock"
    cors_origins: list[str] = ["http://localhost:5173"]
    managed_label: str = "wilson-lab.managed=true"
    seed_demo_users: bool = True
    viewer_username: str = "viewer"
    viewer_password: str = DEFAULT_VIEWER_PASSWORD
    viewer_password_file: str | None = None
    admin_username: str = "admin"
    admin_password: str = DEFAULT_ADMIN_PASSWORD
    admin_password_file: str | None = None
    login_attempt_limit: int = 5
    login_window_seconds: int = 60

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

    @field_validator("access_token_minutes", "login_attempt_limit", "login_window_seconds")
    @classmethod
    def validate_positive_integer(cls, value: int) -> int:
        if value < 1:
            raise ValueError("security timing and limit values must be positive")
        return value

    @model_validator(mode="after")
    def resolve_and_validate_secrets(self):
        self.jwt_secret = self._read_secret(self.jwt_secret_file, self.jwt_secret, "JWT secret")
        self.viewer_password = self._read_secret(
            self.viewer_password_file,
            self.viewer_password,
            "Viewer password",
        )
        self.admin_password = self._read_secret(
            self.admin_password_file,
            self.admin_password,
            "Administrator password",
        )

        if self.environment.lower() == "production":
            if self.jwt_secret == DEFAULT_JWT_SECRET or len(self.jwt_secret) < 32:
                raise ValueError("Production JWT secret must be at least 32 characters")
            if self.seed_demo_users:
                if self.viewer_password == DEFAULT_VIEWER_PASSWORD or len(self.viewer_password) < 16:
                    raise ValueError("Production Viewer password must be at least 16 characters")
                if self.admin_password == DEFAULT_ADMIN_PASSWORD or len(self.admin_password) < 16:
                    raise ValueError("Production Administrator password must be at least 16 characters")
                if self.viewer_password == self.admin_password:
                    raise ValueError("Viewer and Administrator passwords must differ")
        return self

    @staticmethod
    def _read_secret(file_name: str | None, fallback: str, label: str) -> str:
        if not file_name:
            return fallback
        path = Path(file_name)
        try:
            value = path.read_text(encoding="utf-8").strip()
        except OSError as error:
            raise ValueError(f"{label} file could not be read") from error
        if not value:
            raise ValueError(f"{label} file is empty")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
