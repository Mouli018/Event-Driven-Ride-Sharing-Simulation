from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import time
from prometheus_client import Counter, generate_latest
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Ride Request Service")

REQUEST_COUNTER = Counter("ride_requests_total", "Total ride requests made")

class RideRequest(BaseModel):
    user_id: str
    pickup_location: str
    dropoff_location: str

rides_db = {}

@app.post("/request")
def request_ride(ride: RideRequest):
    REQUEST_COUNTER.inc()
    ride_id = str(uuid.uuid4())
    rides_db[ride_id] = {
        "ride_id": ride_id,
        "user_id": ride.user_id,
        "status": "pending",
        "timestamp": time.time()
    }
    # In a real event-driven system, we'd publish this to Kafka/RabbitMQ here
    return {"message": "Ride requested successfully", "ride_id": ride_id}

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest())

@app.get("/health")
def healthz():
    return {"status": "ok"}
