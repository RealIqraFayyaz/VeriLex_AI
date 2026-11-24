from app.ml.ai_signals import analyze
def test_short_text_is_insufficient():
    r=analyze("Short sample.")
    assert r["classification"]=="INSUFFICIENT_EVIDENCE"
    assert r["score"] is None
