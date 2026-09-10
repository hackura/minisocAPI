from fastapi.testclient import TestClient
from app.main import app
from app.config import API_KEY
from app.db import init_db

# TestClient does not run FastAPI startup handlers unless used as a context manager.
# Initialize the development database explicitly for this test suite.
init_db()

client = TestClient(app)
HEADERS = {"X-API-Key": API_KEY}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_event_requires_api_key():
    response = client.get("/api/v1/events")
    assert response.status_code == 401


def test_event_ingestion():
    response = client.post("/api/v1/events", headers=HEADERS, json={
        "event_type": "process_start",
        "username": "analyst",
        "source_ip": "192.0.2.10",
        "message": "Endpoint process started",
    })
    assert response.status_code == 201
    assert response.json()["risk_score"] == 10


def test_bruteforce_detection():
    payload = {
        "event_type": "failed_login",
        "username": "admin",
        "source_ip": "198.51.100.10",
        "message": "Authentication failed",
    }
    for _ in range(5):
        response = client.post("/api/v1/events", headers=HEADERS, json=payload)
    assert response.status_code == 201
    assert response.json()["severity"] == "critical"


def test_alerts_endpoint():
    response = client.get("/api/v1/alerts", headers=HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
