from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config import Settings


def write_secret(path: Path, value: str) -> str:
    path.write_text(value, encoding="utf-8")
    return str(path)


def test_production_settings_load_secrets_from_files(tmp_path: Path):
    settings = Settings(
        _env_file=None,
        environment="production",
        jwt_secret_file=write_secret(tmp_path / "jwt", "j" * 64),
        viewer_password_file=write_secret(tmp_path / "viewer", "viewer-password-12345"),
        admin_password_file=write_secret(tmp_path / "admin", "admin-password-678901"),
    )

    assert settings.jwt_secret == "j" * 64
    assert settings.viewer_password == "viewer-password-12345"
    assert settings.admin_password == "admin-password-678901"


def test_production_rejects_default_secrets():
    with pytest.raises(ValidationError, match="Production JWT secret"):
        Settings(_env_file=None, environment="production")


def test_production_rejects_duplicate_demo_passwords(tmp_path: Path):
    password = "shared-password-12345"
    with pytest.raises(ValidationError, match="must differ"):
        Settings(
            _env_file=None,
            environment="production",
            jwt_secret="j" * 64,
            viewer_password_file=write_secret(tmp_path / "viewer", password),
            admin_password_file=write_secret(tmp_path / "admin", password),
        )


def test_empty_secret_file_is_rejected(tmp_path: Path):
    with pytest.raises(ValidationError, match="JWT secret file is empty"):
        Settings(_env_file=None, jwt_secret_file=write_secret(tmp_path / "jwt", "\n"))
