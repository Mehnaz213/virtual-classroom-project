def _dummy_frame() -> str:
    # tiny 1x1 png pixel
    return (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEUAAACnej3aAAAAAXRS"
        "TlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvDMAAAAASUVORK5CYII="
    )


def auth_headers(client, email="student1@example.com", password="study123"):
    resp = client.post(
        "/api/auth/login/json",
        json={"email": email, "password": password},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_post_frame_records_event(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/events/frame",
        headers=headers,
        json={
            "session_id": 1,
            "attendance_id": 1,
            "frame_b64": _dummy_frame(),
            "labels": [{"name": "focused", "confidence": 0.9}],
            "gaze": {"yaw": 0.0, "pitch": 0.0},
            "head_pose": {"x": 0.0, "y": 0.0, "z": 0.0},
            "face_present": True,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["level"] in {"ENGAGED", "PARTIAL", "NOT_ENGAGED"}


def test_tab_switch_endpoint(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/events/tab-switch",
        headers=headers,
        json={
            "session_id": 1,
            "attendance_id": 1,
            "tab_visible": False,
        },
    )
    assert resp.status_code == 200

