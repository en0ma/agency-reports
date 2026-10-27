def test_schema_lists_every_endpoint(api):
    response = api.get("/api/schema", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert {"/api/health", "/api/me", "/api/cmv-alerts/daily-alerts"} <= set(paths)
