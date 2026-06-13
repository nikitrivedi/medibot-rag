import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, HTTPException

from api.models import LoginRequest, LoginResponse

router = APIRouter(prefix="/api", tags=["auth"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "medibot-dev-secret-change-in-production")
TOKEN_EXPIRE_HOURS = 8

DEMO_USERS = {
    "billing": {"password": "billing123", "role": "billing_executive"},
    "doctor": {"password": "doctor123", "role": "doctor"},
    "nurse": {"password": "nurse123", "role": "nurse"},
    "tech": {"password": "tech123", "role": "technician"},
    "admin": {"password": "admin123", "role": "admin"},
}


def create_session_token(username: str, role: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": username, "role": role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    user = DEMO_USERS.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    role = user["role"]
    return LoginResponse(
        access_token=create_session_token(request.username, role),
        role=role,
        username=request.username,
    )
