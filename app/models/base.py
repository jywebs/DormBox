"""Common base models and types."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class BaseDBModel(BaseModel):
    """Base model for database entities."""
    id: str = Field(alias="_id")
    workspaceId: str
    createdAt: datetime
    updatedAt: datetime