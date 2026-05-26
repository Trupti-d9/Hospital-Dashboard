from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes.analytics import router as analytics_router
from routes.ai_concierge import router as ai_router
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Hospital CEO Dashboard API (Secure & Local)")

# CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Aarogya Hospital CEO Dashboard API is running."}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "sqlite_encrypted", "graph": "neo4j"}

@app.get("/api/mfa/generate")
def generate_mfa_secret():
    """Generates a TOTP secret for the CEO (Run once for setup)."""
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name="CEO@Aarogya", issuer_name="Aarogya Hospital")
    return {"secret": secret, "provisioning_uri": provisioning_uri}

# Register Routes
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Concierge"])
