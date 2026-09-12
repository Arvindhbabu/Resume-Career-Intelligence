"""
ResumeIQ — Authentication & User Identity Routes
Handles user sign-up, login, JWT token issuing, and current user validation.
"""

import base64
import hashlib
import hmac
import json
import time
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from backend.config import get_settings
from backend.database.connection import get_db
from backend.database.models import User, CareerProfile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer(auto_error=False)


# ── Password Hashing Helpers ───────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    settings = get_settings()
    salt = settings.SECRET_KEY.encode('utf-8')
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pw_hash.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hash_password(plain_password) == hashed_password


# ── JWT Helper (Clean HMAC SHA256 Token) ───────────────────────────────────────
def create_access_token(user_id: int, email: str, role: str = "candidate") -> str:
    """Create a signed JSON Web Token."""
    settings = get_settings()
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": int(time.time()) + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    }
    
    b64_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    b64_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature_input = f"{b64_header}.{b64_payload}".encode()
    signature = hmac.new(settings.JWT_SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    b64_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{b64_header}.{b64_payload}.{b64_signature}"

def decode_access_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    settings = get_settings()
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        b64_header, b64_payload, b64_signature = parts
        
        # Verify signature
        signature_input = f"{b64_header}.{b64_payload}".encode()
        expected_sig = hmac.new(settings.JWT_SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(b64_signature + "==")
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        # Decode payload
        payload_bytes = base64.urlsafe_b64decode(b64_payload + "==")
        payload = json.loads(payload_bytes.decode())
        
        if payload.get("exp", 0) < time.time():
            return None  # Expired
        
        return payload
    except Exception as e:
        logger.warning(f"Invalid token decode attempt: {e}")
        return None


# ── Dependency: Get Current User ───────────────────────────────────────────────
async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Dependency returning authenticated user or None if unauthenticated."""
    if not auth or not auth.credentials:
        return None
    
    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        return None
    
    user_id = int(payload["sub"])
    user = db.query(User).filter_by(id=user_id, is_active=True).first()
    return user

async def require_current_user(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Dependency enforcing authentication."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ── Pydantic Request Models ────────────────────────────────────────────────────
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    target_role: Optional[str] = "Software Engineer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Auth Endpoints ─────────────────────────────────────────────────────────────
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    """Register a new candidate user."""
    existing = db.query(User).filter_by(email=req.email).first()
    if existing:
        raise HTTPException(400, "Email is already registered")

    user = User(
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role="candidate",
    )
    db.add(user)
    db.flush()

    # Create associated CareerProfile
    profile = CareerProfile(
        user_id=user.id,
        full_name=req.full_name,
        target_roles=json.dumps([req.target_role or "Software Engineer"]),
    )
    db.add(profile)
    db.commit()

    token = create_access_token(user.id, user.email, user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict(),
        "profile": profile.to_dict(),
    }


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = db.query(User).filter_by(email=req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")

    if not user.is_active:
        raise HTTPException(403, "Account is disabled")

    token = create_access_token(user.id, user.email, user.role)
    profile = db.query(CareerProfile).filter_by(user_id=user.id).first()

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict(),
        "profile": profile.to_dict() if profile else None,
    }


@router.get("/me")
def get_me(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    """Get current authenticated user info and career profile."""
    profile = db.query(CareerProfile).filter_by(user_id=user.id).first()
    return {
        "user": user.to_dict(),
        "profile": profile.to_dict() if profile else None,
    }
