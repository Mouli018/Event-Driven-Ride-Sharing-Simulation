from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_match_driver():
    response = client.post("/match", json={
        "ride_id": "ride-abc-123",
        "pickup_location": "Indiranagar, Bangalore"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["ride_id"] == "ride-abc-123"
    assert "driver" in data
    assert data["status"] == "driver_assigned"

def test_get_status_pending():
    response = client.get("/status/nonexistent-ride")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
