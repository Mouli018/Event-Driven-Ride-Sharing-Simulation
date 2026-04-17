from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import time
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import secrets
import os

app = FastAPI(title="Matching & Status Service")

# Security: CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: Secure Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

MATCH_COUNTER = Counter("driver_matches_total", "Total driver matches made")
MATCH_LATENCY = Histogram("match_latency_seconds", "Time taken to match a driver")

DRIVERS = ["driver_A", "driver_B", "driver_C", "driver_D", "driver_E"]
matches_db = {}

class MatchRequest(BaseModel):
    ride_id: str
    pickup_location: str

@app.post("/match")
def match_driver(req: MatchRequest):
    with MATCH_LATENCY.time():
        # Simulate driver matching delay
        time.sleep(secrets.SystemRandom().uniform(0.1, 0.5))
        assigned_driver = secrets.choice(DRIVERS)
        MATCH_COUNTER.inc()

    matches_db[req.ride_id] = {
        "ride_id": req.ride_id,
        "driver": assigned_driver,
        "status": "driver_assigned",
        "eta_minutes": secrets.SystemRandom().randint(2, 10)
    }
    return matches_db[req.ride_id]

@app.get("/status/{ride_id}")
def get_status(ride_id: str):
    if ride_id not in matches_db:
        return {"ride_id": ride_id, "status": "pending"}
    return matches_db[ride_id]

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest())

@app.get("/health")
def healthz():
    return {"status": "ok"}
