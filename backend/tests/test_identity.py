def test_health_needs_no_identity(api):
    response = api.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rejects_requests_without_a_user(api):
    assert api.get("/api/me").status_code == 401


def test_rejects_unknown_users(api):
    assert api.as_user("mallory").get("/api/me").status_code == 401


def test_me_returns_an_agency_users_single_agency(api):
    response = api.as_user("iowa.analyst").get("/api/me")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "iowa.analyst",
        "display_name": "Iowa analyst",
        "internal": False,
        "agencies": [{"agency": "IA-DOT", "name": "Iowa Department of Transportation"}],
    }


def test_me_returns_every_agency_an_internal_user_may_see(api):
    response = api.as_user("support.staff").get("/api/me")

    assert response.json()["internal"] is True
    # The fixture warehouse only has two of the three agencies support may see.
    assert [a["agency"] for a in response.json()["agencies"]] == ["IA-DOT", "IN-DOT"]


def test_every_response_carries_a_request_id(api):
    response = api.get("/api/health")

    assert response["X-Request-Id"]
