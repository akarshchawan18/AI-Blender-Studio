
import os
import re
from datetime import datetime, timedelta, timezone

import jwt

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import User, SessionLocal, get_db


# =========================================================
# AUTHENTICATION CONFIGURATION
# =========================================================

router = APIRouter(prefix="/auth", tags=["Authentication"])

password_hasher = PasswordHash.recommended()

security = HTTPBearer(auto_error=False)

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def get_jwt_secret():
    """Retrieve the application's secret signing key."""

    secret = os.environ.get("AI_STUDIO_JWT_SECRET")

    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=500,
            detail="Authentication signing secret is not configured correctly."
        )

    return secret


# =========================================================
# REQUEST MODELS
# =========================================================

class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.fullmatch(pattern, value):
            raise ValueError("Enter a valid email address.")

        return value


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower()


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def hash_password(password):
    return password_hasher.hash(password)


def verify_password(plain_password, password_hash):
    return password_hasher.verify(
        plain_password,
        password_hash
    )


# =========================================================
# JWT FUNCTIONS
# =========================================================

def create_access_token(user_id):
    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
        "type": "access",
    }

    return jwt.encode(
        payload,
        get_jwt_secret(),
        algorithm=JWT_ALGORITHM
    )


# =========================================================
# CURRENT CUSTOMER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Validate the bearer token and retrieve its customer."""

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required or token is invalid.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            get_jwt_secret(),
            algorithms=[JWT_ALGORITHM],
        )

        if payload.get("type") != "access":
            raise unauthorized

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise unauthorized

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise unauthorized

    return user


# =========================================================
# USER REGISTRATION
# =========================================================

@router.post("/register")
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = db.scalar(
        select(User).where(User.email == request.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    token = create_access_token(user.id)

    return {
        "status": "success",
        "message": "Account created successfully.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
        },
    }


# =========================================================
# USER LOGIN
# =========================================================

@router.post("/login")
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.email == request.email)
    )

    # Use the same public error for unknown emails and wrong passwords.
    if (
        user is None
        or not user.is_active
        or not verify_password(
            request.password,
            user.password_hash
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id)

    return {
        "status": "success",
        "message": "Login successful.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
        },
    }


# =========================================================
# CURRENT USER ENDPOINT
# =========================================================

@router.get("/me")
def get_my_account(
    current_user: User = Depends(get_current_user),
):
    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat(),
            "is_active": current_user.is_active,
        },
    }
