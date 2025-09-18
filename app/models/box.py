"""Box models."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from .base import BaseDBModel

class BoxCreate(BaseModel):
    """Model for creating a new box."""
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    tags: List[str] = []
    sourceLocation: Optional[str] = None
    destination: Optional[str] = None
    status: str = Field("planned", pattern="^(planned|packed|shipped|arrived)$")

class BoxUpdate(BaseModel):
    """Model for updating a box."""
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    sourceLocation: Optional[str] = None
    destination: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(planned|packed|shipped|arrived)$")

class Box(BaseDBModel):
    """Model representing a box."""
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    sourceLocation: Optional[str] = None
    destination: Optional[str] = None
    status: str
    qrSlug: str
    createdBy: str

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "workspaceId": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "name": "Kitchen Supplies",
                "description": "All kitchen related items",
                "tags": ["kitchen", "appliances"],
                "sourceLocation": "Home",
                "destination": "Dorm Room 123",
                "status": "planned",
                "qrSlug": "abc123xyz",
                "createdBy": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "createdAt": "2023-09-16T12:00:00Z",
                "updatedAt": "2023-09-16T12:00:00Z"
            }
        }