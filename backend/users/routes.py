from models import FollowedDataset, DatasetCombination
from sqlmodel import select, Session
from fastapi import APIRouter, Depends, HTTPException
from auth.routes import get_current_user
from database import engine
from models import User
from pydantic import BaseModel
from auth.routes import _hf_cache
from typing import List, Optional

router = APIRouter()

class FollowRequest(BaseModel):
    dataset_id: str

class DatasetCombinationRequest(BaseModel):
    name: str
    dataset_ids: List[str]
    description: Optional[str] = None

@router.post("/user/follow")
def follow_dataset(
    data: FollowRequest,
    current_user: User = Depends(get_current_user)
):
    with Session(engine) as session:
        # Prevent duplicate follows
        existing = session.exec(
            select(FollowedDataset).where(
                (FollowedDataset.user_id == current_user.id) &
                (FollowedDataset.dataset_id == data.dataset_id)
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Already following this dataset")
        follow = FollowedDataset(user_id=current_user.id, dataset_id=data.dataset_id)
        session.add(follow)
        session.commit()
        session.refresh(follow)
        return {"message": "Dataset followed", "follow_id": follow.id}

@router.get("/user/followed")
def get_followed_datasets(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        follows = session.exec(
            select(FollowedDataset).where(FollowedDataset.user_id == current_user.id)
        ).all()
        if not follows:
            return []

        # Get cached datasets
        cached = _hf_cache["data"] or []
        # Build a dict for fast lookup
        cached_dict = {ds["id"]: ds for ds in cached}

        # Join followed datasets with cached metadata
        result = []
        for follow in follows:
            meta = cached_dict.get(follow.dataset_id)
            if meta:
                result.append(meta)
            else:
                # If not in cache, just return the id
                result.append({"id": follow.dataset_id, "description": "No metadata (not in cache)"})
        return result

@router.delete("/user/follow/{dataset_id:path}")
def unfollow_dataset(dataset_id: str, current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        follow = session.exec(
            select(FollowedDataset).where(
                (FollowedDataset.user_id == current_user.id) &
                (FollowedDataset.dataset_id == dataset_id)
            )
        ).first()
        if not follow:
            raise HTTPException(status_code=404, detail="Not following this dataset")
        session.delete(follow)
        session.commit()
        return {"message": "Unfollowed"}

@router.post("/datasets/combine")
def create_dataset_combination(
    data: DatasetCombinationRequest,
    current_user: User = Depends(get_current_user)
):
    with Session(engine) as session:
        # Create new combination
        combination = DatasetCombination(
            user_id=current_user.id,
            name=data.name,
            description=data.description
        )
        combination.set_dataset_ids(data.dataset_ids)
        session.add(combination)
        session.commit()
        session.refresh(combination)
        return combination

@router.get("/datasets/combinations")
def get_user_combinations(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        combinations = session.exec(
            select(DatasetCombination).where(DatasetCombination.user_id == current_user.id)
        ).all()
        
        # Get cached datasets for metadata
        cached = _hf_cache["data"] or []
        cached_dict = {ds["id"]: ds for ds in cached}
        
        # Enrich combinations with dataset metadata
        result = []
        for combo in combinations:
            enriched_datasets = []
            for dataset_id in combo.get_dataset_ids():
                meta = cached_dict.get(dataset_id)
                if meta:
                    enriched_datasets.append(meta)
                else:
                    enriched_datasets.append({"id": dataset_id, "description": "No metadata (not in cache)"})
            
            result.append({
                "id": combo.id,
                "name": combo.name,
                "description": combo.description,
                "created_at": combo.created_at,
                "datasets": enriched_datasets
            })
        
        return result
