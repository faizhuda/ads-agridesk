from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "X-Request-ID" in response.headers


def test_ready_endpoint_returns_ready():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_rate_limit_blocks_after_threshold():
    limiter = app.state.rate_limiter
    original_max = limiter.max_requests
    original_window = limiter.window_seconds

    try:
        limiter.reset()
        limiter.max_requests = 2
        limiter.window_seconds = 60

        first = client.get("/")
        second = client.get("/")
        third = client.get("/")

        assert first.status_code == 200
        assert second.status_code == 200
        assert third.status_code == 429
        assert third.json()["detail"] == "Rate limit exceeded"
        assert third.headers.get("Retry-After") is not None
    finally:
        limiter.reset()
        limiter.max_requests = original_max
        limiter.window_seconds = original_window
