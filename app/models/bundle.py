"""Bundle models."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from .base import BaseDBModel

class BundleCreate(BaseModel):
    """Model for creating a new bundle."""
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    tags: List[str] = []
    itemIds: List[str] = []

class BundleUpdate(BaseModel):
    """Model for updating a bundle."""
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class Bundle(BaseDBModel):
    """Model representing a bundle."""
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    itemIds: List[str] = []
    itemCount: int
    createdBy: str

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "workspaceId": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "name": "Kitchen Essentials",
                "description": "Basic kitchen supplies needed for dorm",
                "tags": ["kitchen", "essentials"],
                "itemIds": ["5f7b5e7b5e7b5e7b5e7b5e7b"],
                "itemCount": 1,
                "createdBy": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "createdAt": "2023-09-16T12:00:00Z",
                "updatedAt": "2023-09-16T12:00:00Z"
            }
        }