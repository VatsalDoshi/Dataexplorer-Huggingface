from fastapi import APIRouter, HTTPException, status, Depends, Request, Header, Body
from sqlmodel import Session, select
from models import User
from database import engine
from .utils import get_password_hash, create_tokens, verify_password, verify_token
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import time
import datetime
import math
from sklearn.cluster import KMeans, DBSCAN
import numpy as np

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: str

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ImpactRequest(BaseModel):
    datasets: list
    method: str = 'naive'  # 'naive' or 'advanced'

# Dependency to get current user from JWT token
async def get_current_user(authorization: str = Header(...)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)):
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User ID is missing")
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=str(current_user.created_at)
    )

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate):
    # Check if user already exists
    with Session(engine) as session:
        existing_user = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # Create tokens
        access_token, refresh_token = create_tokens(
            data={"sub": new_user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin):
    with Session(engine) as session:
        # Find user by email
        user = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token, refresh_token = create_tokens(
            data={"sub": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

@router.post("/refresh", response_model=RefreshResponse)
def refresh_token(data: RefreshRequest = Body(...)):
    try:
        payload = verify_token(data.refresh_token, is_refresh=True)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        # Optionally, you can check if the user still exists/is active
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            # Issue new tokens
            access_token, refresh_token = create_tokens({"sub": user.email})
            return RefreshResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/datasets/impact")
async def assess_impact(data: ImpactRequest = Body(...)):
    datasets = data.datasets
    method = data.method
    results = []
    explanation = ""

    if method == 'naive':
        explanation = "Naive impact is assigned based on size_mb: <100MB=low, <1000MB=medium, >=1000MB=high."
        for ds in datasets:
            size_mb = ds.get('size_mb', 0)
            if size_mb < 100:
                impact = 'low'
            elif size_mb < 1000:
                impact = 'medium'
            else:
                impact = 'high'
            results.append({"id": ds.get("id"), "impact": impact, "explanation": explanation})
    elif method == 'advanced':
        explanation = "Advanced impact uses KMeans clustering on [size_mb, num_rows, num_columns]; outliers (top 5% farthest from cluster center) are 'high impact'."
        features = [
            [ds.get('size_mb', 0), ds.get('num_rows', 0), ds.get('num_columns', 0)]
            for ds in datasets
        ]
        X = np.array(features)
        if len(X) >= 3:
            kmeans = KMeans(n_clusters=3, random_state=0)
            labels = kmeans.fit_predict(X)
            distances = np.linalg.norm(X - kmeans.cluster_centers_[labels], axis=1)
            threshold = np.percentile(distances, 95)
            for i, ds in enumerate(datasets):
                if distances[i] > threshold:
                    impact = 'high impact'
                else:
                    impact = 'normal'
                results.append({"id": ds.get("id"), "impact": impact, "explanation": explanation})
        else:
            for ds in datasets:
                results.append({"id": ds.get("id"), "impact": "normal", "explanation": "Not enough data for clustering."})
    else:
        return {"error": "Unknown method. Use 'naive' or 'advanced'."}
    return {"results": results, "method": method}

# Global cache
_hf_cache = {
    "data": None,
    "timestamp": 0
}
CACHE_TTL = 30 * 60  # 30 minutes in seconds

def get_impact_label_from_size_category(size_category):
    if "10K<n<100K" in size_category:
        return "low"
    elif "100K<n<1M" in size_category:
        return "medium"
    elif "1M<n<10M" in size_category or "10M<n" in size_category or "100M<n" in size_category or "1B<n" in size_category:
        return "high"
    else:
        return "low"  # default fallback

def generate_mock_metadata(ds):
    # You can randomize or use deterministic values for demo
    import random
    return {
        "size_mb": random.uniform(10, 2000),
        "num_rows": random.randint(1000, 1000000),
        "num_columns": random.randint(5, 100)
    }

@router.get("/datasets", tags=["public"])
async def get_hf_datasets():
    now = time.time()
    if _hf_cache["data"] and (now - _hf_cache["timestamp"] < CACHE_TTL):
        time_left = CACHE_TTL - (now - _hf_cache["timestamp"])
        print(f"[CACHE] Returning cached datasets. Time left: {math.ceil(time_left)} seconds")
        return _hf_cache["data"]

    url = "https://huggingface.co/api/datasets"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        datasets = response.json()
        trimmed = []
        features = []
        for ds in datasets:
            meta = generate_mock_metadata(ds)
            features.append([meta["size_mb"], meta["num_rows"], meta["num_columns"]])
            trimmed.append({
                "id": ds.get("id"),
                "description": ds.get("description"),
                "downloads": ds.get("downloads"),
                "likes": ds.get("likes"),
                "lastModified": ds.get("lastModified"),
                "size_mb": meta["size_mb"],
                "num_rows": meta["num_rows"],
                "num_columns": meta["num_columns"],
            })

        # Clustering (KMeans example)
        X = np.array(features)
        if len(X) >= 3:  # KMeans needs at least as many samples as clusters
            kmeans = KMeans(n_clusters=3, random_state=0)
            labels = kmeans.fit_predict(X)
            # Compute distances to cluster centers
            distances = np.linalg.norm(X - kmeans.cluster_centers_[labels], axis=1)
            threshold = np.percentile(distances, 95)  # top 5% as outliers
            for i, ds in enumerate(trimmed):
                ds["cluster"] = int(labels[i])
                if distances[i] > threshold:
                    ds["impact"] = "high impact"
                else:
                    ds["impact"] = "normal"
        else:
            for ds in trimmed:
                ds["cluster"] = 0
                ds["impact"] = "normal"

        _hf_cache["data"] = trimmed
        _hf_cache["timestamp"] = now
        print("[CACHE] Cache expired or empty. Fetching new data from HuggingFace.")
        return trimmed

@router.get("/datasets/cache_status")
def cache_status():
    return {
        "cached": _hf_cache["data"] is not None,
        "last_updated": (
            datetime.datetime.fromtimestamp(_hf_cache["timestamp"]).isoformat()
            if _hf_cache["timestamp"] else None
        )
    } 