def test_teacher_can_login(client):
    response = client.post(
        "/api/auth/login/json",
        json={"email": "teacher@example.com", "password": "teach123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_me_endpoint_returns_profile(client):
    token = client.post(
        "/api/auth/login/json",
        json={"email": "teacher@example.com", "password": "teach123"},
    ).json()["access_token"]
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "teacher@example.com"
