def test_inventory_requires_authentication(client):
    response = client.get("/api/v1/inventory")

    assert response.status_code == 401


def test_viewer_can_list_managed_resources(client, viewer_headers):
    response = client.get("/api/v1/inventory", headers=viewer_headers)

    assert response.status_code == 200
    resources = response.json()
    assert {resource["id"] for resource in resources} == {
        "demo-grafana",
        "demo-juice-shop",
    }
    assert all("allowed_actions" in resource for resource in resources)


def test_viewer_can_open_resource_detail(client, viewer_headers):
    response = client.get(
        "/api/v1/inventory/demo-grafana",
        headers=viewer_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Grafana"


def test_unknown_resource_returns_not_found(client, viewer_headers):
    response = client.get(
        "/api/v1/inventory/not-managed",
        headers=viewer_headers,
    )

    assert response.status_code == 404
