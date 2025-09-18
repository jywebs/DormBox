"""Item models."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from .base import BaseDBModel

class ItemCreate(BaseModel):
    """Model for creating a new item."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: int = Field(1, ge=1)
    category: Optional[str] = None
    estimatedValue: Optional[float] = Field(None, ge=0)
    imageUrl: Optional[HttpUrl] = None
    amazonUrl: Optional[HttpUrl] = None
    asin: Optional[str] = None
    boxId: str
    bundleIds: List[str] = []
    status: str = Field("planned", pattern="^(planned|packed|arrived)$")
    notes: Optional[str] = None

class ItemUpdate(BaseModel):
    """Model for updating an item."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=1)
    category: Optional[str] = None
    estimatedValue: Optional[float] = Field(None, ge=0)
    imageUrl: Optional[HttpUrl] = None
    amazonUrl: Optional[HttpUrl] = None
    asin: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(planned|packed|arrived)$")
    notes: Optional[str] = None

class ItemMove(BaseModel):
    """Model for moving an item to a different box."""
    boxId: str

class Item(BaseDBModel):
    """Model representing an item."""
    title: str
    description: Optional[str] = None
    quantity: int
    category: Optional[str] = None
    estimatedValue: Optional[float] = None
    imageUrl: Optional[HttpUrl] = None
    amazonUrl: Optional[HttpUrl] = None
    asin: Optional[str] = None
    boxId: str
    bundleIds: List[str] = []
    status: str
    notes: Optional[str] = None

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "workspaceId": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "title": "Electric Kettle",
                "description": "1.7L stainless steel kettle",
                "quantity": 1,
                "category": "appliances",
                "estimatedValue": 29.99,
                "imageUrl": "https://example.com/image.jpg",
                "amazonUrl": "https://amazon.com/dp/B12345678",
                "asin": "B12345678",
                "boxId": "5f7b5e7b5e7b5e7b5e7b5e7b",
                "bundleIds": ["5f7b5e7b5e7b5e7b5e7b5e7b"],
                "status": "planned",
                "notes": "Remember to pack power cord",
                "createdAt": "2023-09-16T12:00:00Z",
                "updatedAt": "2023-09-16T12:00:00Z"
            }
        }