def test_health_is_public(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "environment": "test",
        "runtime": "mock",
    }


def test_bad_login_is_rejected(client):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "viewer", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_viewer_can_read_identity(client, viewer_headers):
    response = client.get("/api/v1/auth/me", headers=viewer_headers)

    assert response.status_code == 200
    assert response.json()["username"] == "viewer"
    assert response.json()["role"] == "viewer"
