"""Item router module."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import Database
from app.db.helpers import DBHelper
from app.models.item import Item, ItemCreate, ItemUpdate, ItemMove
from app.services.enrichment_service import EnrichmentService

router = APIRouter()

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    workspace_id: str = Query(..., description="Workspace ID"),
    payload: ItemCreate = ...,
    db = Depends(Database.get_db)
) -> Item:
    """Create a new item."""
    try:
        # Verify box exists
        box = await DBHelper.find_document("boxes", workspace_id, payload.boxId)
        if not box:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "box_not_found", "message": "Box not found"}}
            )

        # Verify bundles exist if specified
        for bundle_id in payload.bundleIds:
            bundle = await DBHelper.find_document("bundles", workspace_id, bundle_id)
            if not bundle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": {"code": "bundle_not_found", "message": f"Bundle {bundle_id} not found"}}
                )

        # Create item document
        doc = await DBHelper.create_document(
            "items",
            workspace_id,
            payload.dict(exclude_unset=True)
        )
        return Item(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "create_failed", "message": str(e)}}
        )

@router.get("/", response_model=List[Item])
async def list_items(
    workspace_id: str = Query(..., description="Workspace ID"),
    q: Optional[str] = Query(None, description="Search query"),
    box_id: Optional[str] = Query(None, description="Filter by box ID"),
    bundle_id: Optional[str] = Query(None, description="Filter by bundle ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db = Depends(Database.get_db)
) -> List[Item]:
    """List items with optional filtering."""
    filters = {}
    if q:
        filters["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
        ]
    if box_id:
        filters["boxId"] = box_id
    if bundle_id:
        filters["bundleIds"] = bundle_id
    if status:
        filters["status"] = status

    try:
        docs = await DBHelper.list_documents(
            "items",
            workspace_id,
            filters=filters,
            skip=skip,
            limit=limit,
            sort=[("updatedAt", -1)]
        )
        return [Item(**doc) for doc in docs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "list_failed", "message": str(e)}}
        )

@router.get("/{item_id}", response_model=Item)
async def get_item(
    workspace_id: str = Query(..., description="Workspace ID"),
    item_id: str = ...,
    db = Depends(Database.get_db)
) -> Item:
    """Get a specific item by ID."""
    doc = await DBHelper.find_document("items", workspace_id, item_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Item not found"}}
        )
    return Item(**doc)

@router.patch("/{item_id}", response_model=Item)
async def update_item(
    workspace_id: str,
    item_id: str,
    payload: ItemUpdate,
    db = Depends(Database.get_db)
) -> Item:
    """Update an item."""
    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "no_updates", "message": "No updates provided"}}
        )

    doc = await DBHelper.update_document("items", workspace_id, item_id, update_data)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Item not found"}}
        )
    return Item(**doc)

@router.patch("/{item_id}/move", response_model=Item)
async def move_item(
    workspace_id: str,
    item_id: str,
    payload: ItemMove,
    db = Depends(Database.get_db)
) -> Item:
    """Move an item to a different box."""
    # Verify target box exists
    box = await DBHelper.find_document("boxes", workspace_id, payload.boxId)
    if not box:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "box_not_found", "message": "Target box not found"}}
        )

    # Update item's box
    doc = await DBHelper.update_document(
        "items",
        workspace_id,
        item_id,
        {"boxId": payload.boxId}
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Item not found"}}
        )
    return Item(**doc)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    workspace_id: str,
    item_id: str,
    db = Depends(Database.get_db)
):
    """Delete an item."""
    success = await DBHelper.delete_document("items", workspace_id, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Item not found"}}
        )