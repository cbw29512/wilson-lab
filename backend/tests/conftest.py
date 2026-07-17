import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DATABASE = Path("wilson_lab_test.db")
TEST_DATABASE.unlink(missing_ok=True)

os.environ["WILSON_LAB_ENVIRONMENT"] = "test"
os.environ["WILSON_LAB_DATABASE_URL"] = "sqlite:///./wilson_lab_test.db"
os.environ["WILSON_LAB_JWT_SECRET"] = "test-secret-that-is-not-used-outside-ci"
os.environ["WILSON_LAB_RUNTIME_MODE"] = "mock"
os.environ["WILSON_LAB_VIEWER_PASSWORD"] = "viewer-test-password"
os.environ["WILSON_LAB_ADMIN_PASSWORD"] = "admin-test-password"

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def login(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def viewer_headers(client: TestClient) -> dict[str, str]:
    token = login(client, "viewer", "viewer-test-password")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    token = login(client, "admin", "admin-test-password")
    return {"Authorization": f"Bearer {token}"}
