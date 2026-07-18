from fastapi.testclient import TestClient

from app.rate_limit import LoginRateLimiter


def test_readiness_checks_database_and_runtime(client: TestClient):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ok",
        "runtime": "mock",
        "managed_resources": 2,
    }


def test_request_context_headers_are_added(client: TestClient):
    first = client.get("/health")
    second = client.get("/health")

    assert first.status_code == 200
    assert len(first.headers["x-request-id"]) == 32
    assert first.headers["x-request-id"] != second.headers["x-request-id"]
    assert first.headers["x-content-type-options"] == "nosniff"


def test_api_responses_disable_caching(client: TestClient):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "unknown-user", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.headers["cache-control"] == "no-store"
    assert len(response.headers["x-request-id"]) == 32


def test_failed_login_limit_returns_retry_after(client: TestClient):
    for _ in range(4):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "rate-limit-probe", "password": "wrong-password"},
        )
        assert response.status_code == 401

    blocked = client.post(
        "/api/v1/auth/token",
        data={"username": "rate-limit-probe", "password": "wrong-password"},
    )

    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Too many login attempts. Try again later."
    assert int(blocked.headers["retry-after"]) >= 1


def test_limiter_resets_and_expires_failures():
    now = [100.0]
    limiter = LoginRateLimiter(
        attempt_limit=2,
        window_seconds=10,
        clock=lambda: now[0],
    )
    key = limiter.key("203.0.113.5", "Viewer")

    assert limiter.register_failure(key).allowed is True
    blocked = limiter.register_failure(key)
    assert blocked.allowed is False
    assert blocked.retry_after == 10

    limiter.reset(key)
    assert limiter.check(key).allowed is True

    limiter.register_failure(key)
    now[0] = 111.0
    assert limiter.check(key).allowed is True
