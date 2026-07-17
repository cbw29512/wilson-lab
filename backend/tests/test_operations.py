def test_viewer_cannot_operate_resources(client, viewer_headers):
    response = client.post(
        "/api/v1/resources/demo-grafana/operations",
        headers=viewer_headers,
        json={"action": "stop", "confirmed": True},
    )

    assert response.status_code == 403


def test_admin_must_confirm_operation(client, admin_headers):
    response = client.post(
        "/api/v1/resources/demo-grafana/operations",
        headers=admin_headers,
        json={"action": "stop", "confirmed": False},
    )

    assert response.status_code == 409


def test_admin_can_stop_managed_resource_and_view_audit(client, admin_headers):
    response = client.post(
        "/api/v1/resources/demo-grafana/operations",
        headers=admin_headers,
        json={"action": "stop", "confirmed": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "succeeded"
    assert payload["resource"]["status"] == "stopped"
    assert payload["resource"]["allowed_actions"] == ["start"]

    audit = client.get("/api/v1/audit", headers=admin_headers)
    assert audit.status_code == 200
    assert any(
        event["resource_id"] == "demo-grafana"
        and event["outcome"] == "succeeded"
        for event in audit.json()
    )


def test_invalid_state_transition_is_audited(client, admin_headers):
    first = client.post(
        "/api/v1/resources/demo-grafana/operations",
        headers=admin_headers,
        json={"action": "stop", "confirmed": True},
    )
    assert first.status_code == 200

    repeated = client.post(
        "/api/v1/resources/demo-grafana/operations",
        headers=admin_headers,
        json={"action": "stop", "confirmed": True},
    )
    assert repeated.status_code == 409

    audit = client.get("/api/v1/audit", headers=admin_headers)
    assert any(event["outcome"] == "failed" for event in audit.json())
