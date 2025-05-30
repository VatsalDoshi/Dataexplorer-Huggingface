from datetime import datetime, timedelta
from typing import Optional, Tuple
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "your-refresh-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_tokens(data: dict) -> Tuple[str, str]:
    """Create both access and refresh tokens."""
    to_encode = data.copy()
    
    # Create access token
    access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_to_encode = to_encode.copy()
    access_to_encode.update({"exp": access_expire})
    access_token = jwt.encode(access_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Create refresh token
    refresh_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_to_encode = to_encode.copy()
    refresh_to_encode.update({"exp": refresh_expire})
    refresh_token = jwt.encode(refresh_to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token

def verify_token(token: str, is_refresh: bool = False) -> dict:
    """Verify a JWT token and return its payload."""
    try:
        secret_key = REFRESH_SECRET_KEY if is_refresh else SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) 