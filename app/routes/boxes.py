"""Box router module."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import Database
from app.db.helpers import DBHelper
from app.models.box import Box, BoxCreate, BoxUpdate
from app.services.qr_service import QRService

router = APIRouter()

@router.post("/", response_model=Box, status_code=status.HTTP_201_CREATED)
async def create_box(
    workspace_id: str,
    payload: BoxCreate,
    db = Depends(Database.get_db)
) -> Box:
    """Create a new box."""
    try:
        # Generate unique QR slug
        slug = str(uuid.uuid4())
        
        # Create box document
        doc = await DBHelper.create_document(
            "boxes",
            workspace_id,
            {
                "name": payload.name,
                "description": payload.description,
                "tags": payload.tags,
                "sourceLocation": payload.sourceLocation,
                "destination": payload.destination,
                "status": payload.status,
                "qrSlug": slug,
                "createdBy": "TODO"  # Will be set from auth token
            }
        )
        return Box(**doc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "create_failed", "message": str(e)}}
        )

@router.get("/", response_model=List[Box])
async def list_boxes(
    workspace_id: str,
    q: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db = Depends(Database.get_db)
) -> List[Box]:
    """List boxes with optional filtering."""
    filters = {}
    if q:
        filters["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
        ]
    if status:
        filters["status"] = status

    try:
        docs = await DBHelper.list_documents(
            "boxes",
            workspace_id,
            filters=filters,
            skip=skip,
            limit=limit,
            sort=[("updatedAt", -1)]
        )
        return [Box(**doc) for doc in docs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "list_failed", "message": str(e)}}
        )

@router.get("/{box_id}", response_model=Box)
async def get_box(
    workspace_id: str,
    box_id: str,
    db = Depends(Database.get_db)
) -> Box:
    """Get a specific box by ID."""
    doc = await DBHelper.find_document("boxes", workspace_id, box_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Box not found"}}
        )
    return Box(**doc)

@router.patch("/{box_id}", response_model=Box)
async def update_box(
    workspace_id: str,
    box_id: str,
    payload: BoxUpdate,
    db = Depends(Database.get_db)
) -> Box:
    """Update a box."""
    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "no_updates", "message": "No updates provided"}}
        )

    doc = await DBHelper.update_document("boxes", workspace_id, box_id, update_data)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Box not found"}}
        )
    return Box(**doc)

@router.delete("/{box_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_box(
    workspace_id: str,
    box_id: str,
    db = Depends(Database.get_db)
):
    """Delete a box."""
    success = await DBHelper.delete_document("boxes", workspace_id, box_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Box not found"}}
        )

@router.get("/qr/{slug}", response_model=Box)
async def get_box_by_qr(
    slug: str,
    workspace_id: Optional[str] = None,
    db = Depends(Database.get_db)
) -> Box:
    """Get a box by its QR slug."""
    query = {"qrSlug": slug}
    if workspace_id:
        query["workspaceId"] = workspace_id

    doc = await db.boxes.find_one(query)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Box not found"}}
        )
    doc["_id"] = str(doc["_id"])
    return Box(**doc)