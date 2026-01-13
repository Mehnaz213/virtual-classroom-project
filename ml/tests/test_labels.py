from ml.labels import label_from_outputs, one_hot, LABELS


def test_label_mapping_focused():
    label = label_from_outputs(0.5, -0.2, eyes_open_prob=0.9, multiple_faces=False, confidence=0.9)
    assert label == "focused"


def test_label_mapping_sleepy():
    label = label_from_outputs(0.0, 0.0, eyes_open_prob=0.05, multiple_faces=False, confidence=0.9)
    assert label == "sleepy"


def test_label_mapping_low_confidence():
    label = label_from_outputs(20.0, 3.0, eyes_open_prob=0.9, multiple_faces=False, confidence=0.1)
    assert label == "unknown"


def test_one_hot_length():
    vec = one_hot("looking_left")
    assert len(vec) == len(LABELS)
    assert sum(vec) == 1.0


