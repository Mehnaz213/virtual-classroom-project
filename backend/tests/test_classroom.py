def auth_headers(client, email="teacher@example.com", password="teach123"):
    resp = client.post(
        "/api/auth/login/json",
        json={"email": email, "password": password},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_returns_data(client):
    headers = auth_headers(client)
    resp = client.get("/api/class/1/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == 1
    assert "attendance" in data
    assert "timeline" in data


def test_teacher_can_create_and_list_session(client):
    headers = auth_headers(client)
    create_resp = client.post("/api/class/create", json={"topic": "Geometry"}, headers=headers)
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]

    list_resp = client.get("/api/class/mine", headers=headers)
    assert list_resp.status_code == 200
    assert any(session["id"] == session_id for session in list_resp.json())


def test_student_join_validates_code(client):
    teacher_headers = auth_headers(client)
    session_resp = client.post("/api/class/create", json={"topic": "Biology"}, headers=teacher_headers)
    session = session_resp.json()

    student_headers = auth_headers(client, email="student1@example.com", password="study123")
    wrong_code_resp = client.post(
        f"/api/class/{session['id']}/join",
        headers=student_headers,
        json={"code": "WRONG", "lock_mode": False},
    )
    assert wrong_code_resp.status_code == 400

    correct_resp = client.post(
        f"/api/class/{session['id']}/join",
        headers=student_headers,
        json={"code": session["code"], "lock_mode": True},
    )
    assert correct_resp.status_code == 200
    assert correct_resp.json()["lock_mode"] is True

