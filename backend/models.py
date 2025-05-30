from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import json

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

class FollowedDataset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    dataset_id: str  # HuggingFace dataset id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Optionally, add a unique constraint on (user_id, dataset_id) 

class DatasetCombination(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    dataset_ids: str = Field(default="[]")  # Store as JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = None

    def get_dataset_ids(self) -> List[str]:
        return json.loads(self.dataset_ids)

    def set_dataset_ids(self, ids: List[str]):
        self.dataset_ids = json.dumps(ids) 