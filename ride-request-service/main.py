from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import time
from prometheus_client import Counter, generate_latest
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os

# Production Hardening: Disable docs in production/CI
app = FastAPI(
    title="Ride Request Service",
    docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
    redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc"
)

# Security: Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]  # Restrict this in production
)

# Security: CORS Policy (Standard Hotspot Fix)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your dashboard domain
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
