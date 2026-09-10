from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_event_ingestion():
    response = client.post("/api/v1/events", json={
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
        response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 201
    assert response.json()["severity"] == "critical"
