from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ride-request"}

def test_request_ride_success():
    response = client.post("/request", json={
        "user_id": "user_123",
        "pickup_location": "MG Road, Bangalore",
        "dropoff_location": "Koramangala, Bangalore"
    })
    assert response.status_code == 200
    data = response.json()
    assert "ride_id" in data
    assert data["message"] == "Ride requested successfully"

def test_request_ride_missing_field():
    response = client.post("/request", json={
        "user_id": "user_123",
        "pickup_location": "MG Road"
        # missing dropoff_location
    })
    assert response.status_code == 422  # Validation error
