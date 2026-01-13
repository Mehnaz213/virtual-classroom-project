from app.core import engagement


def test_engagement_fallback_without_frame():
    result = engagement.summarize_frame(None)
    assert result.level in {"ENGAGED", "PARTIAL", "NOT_ENGAGED"}

