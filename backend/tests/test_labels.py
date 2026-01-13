from app.core.labels import derive_attention_labels


def test_labels_focused():
    labels = derive_attention_labels(
        gaze_yaw=0.0,
        gaze_pitch=0.0,
        head_yaw=0.0,
        head_pitch=0.0,
        eyes_open_prob=0.9,
        face_present=True,
        multi_face=False,
    )
    names = {item["name"] for item in labels}
    assert "focused" in names
    assert "engaged" in names


def test_labels_sleepy():
    labels = derive_attention_labels(
        gaze_yaw=30,
        gaze_pitch=0.0,
        head_yaw=10,
        head_pitch=0.0,
        eyes_open_prob=0.1,
        face_present=True,
        multi_face=True,
    )
    names = {item["name"] for item in labels}
    assert "sleepy" in names
    assert "distracted_by_multi_face" in names

