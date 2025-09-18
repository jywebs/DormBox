"""Bundle router module."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import Database
from app.db.helpers import DBHelper
from app.models.bundle import Bundle, BundleCreate, BundleUpdate

router = APIRouter()

@router.post("/", response_model=Bundle, status_code=status.HTTP_201_CREATED)
async def create_bundle(
    workspace_id: str,
    payload: BundleCreate,
    db = Depends(Database.get_db)
) -> Bundle:
    """Create a new bundle."""
    try:
        # Verify items exist if specified
        for item_id in payload.itemIds:
            item = await DBHelper.find_document("items", workspace_id, item_id)
            if not item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": {"code": "item_not_found", "message": f"Item {item_id} not found"}}
                )

        # Create bundle document
        doc = await DBHelper.create_document(
            "bundles",
            workspace_id,
            {
                "name": payload.name,
                "description": payload.description,
                "tags": payload.tags,
                "itemIds": payload.itemIds,
                "itemCount": len(payload.itemIds),
                "createdBy": "TODO"  # Will be set from auth token
            }
        )
        return Bundle(**doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "create_failed", "message": str(e)}}
        )

@router.get("/", response_model=List[Bundle])
async def list_bundles(
    workspace_id: str,
    q: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db = Depends(Database.get_db)
) -> List[Bundle]:
    """List bundles with optional filtering."""
    filters = {}
    if q:
        filters["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
        ]

    try:
        docs = await DBHelper.list_documents(
            "bundles",
            workspace_id,
            filters=filters,
            skip=skip,
            limit=limit,
            sort=[("updatedAt", -1)]
        )
        return [Bundle(**doc) for doc in docs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "list_failed", "message": str(e)}}
        )

@router.get("/{bundle_id}", response_model=Bundle)
async def get_bundle(
    workspace_id: str,
    bundle_id: str,
    db = Depends(Database.get_db)
) -> Bundle:
    """Get a specific bundle by ID."""
    doc = await DBHelper.find_document("bundles", workspace_id, bundle_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Bundle not found"}}
        )
    return Bundle(**doc)

@router.patch("/{bundle_id}", response_model=Bundle)
async def update_bundle(
    workspace_id: str,
    bundle_id: str,
    payload: BundleUpdate,
    db = Depends(Database.get_db)
) -> Bundle:
    """Update a bundle."""
    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "no_updates", "message": "No updates provided"}}
        )

    doc = await DBHelper.update_document("bundles", workspace_id, bundle_id, update_data)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Bundle not found"}}
        )
    return Bundle(**doc)

@router.post("/{bundle_id}/items/{item_id}")
async def add_item_to_bundle(
    workspace_id: str,
    bundle_id: str,
    item_id: str,
    db = Depends(Database.get_db)
):
    """Add an item to a bundle."""
    # Verify both bundle and item exist
    bundle = await DBHelper.find_document("bundles", workspace_id, bundle_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Bundle not found"}}
        )

    item = await DBHelper.find_document("items", workspace_id, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Item not found"}}
        )

    # Update bundle and item
    if item_id not in bundle["itemIds"]:
        await DBHelper.update_document(
            "bundles",
            workspace_id,
            bundle_id,
            {
                "itemIds": bundle["itemIds"] + [item_id],
                "itemCount": len(bundle["itemIds"]) + 1
            }
        )

    if bundle_id not in item.get("bundleIds", []):
        await DBHelper.update_document(
            "items",
            workspace_id,
            item_id,
            {"bundleIds": item.get("bundleIds", []) + [bundle_id]}
        )

@router.delete("/{bundle_id}/items/{item_id}")
async def remove_item_from_bundle(
    workspace_id: str,
    bundle_id: str,
    item_id: str,
    db = Depends(Database.get_db)
):
    """Remove an item from a bundle."""
    # Verify both bundle and item exist
    bundle = await DBHelper.find_document("bundles", workspace_id, bundle_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Bundle not found"}}
        )

    item = await DBHelper.find_document("items", workspace_id, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Item not found"}}
        )

    # Update bundle and item
    if item_id in bundle["itemIds"]:
        await DBHelper.update_document(
            "bundles",
            workspace_id,
            bundle_id,
            {
                "itemIds": [i for i in bundle["itemIds"] if i != item_id],
                "itemCount": len(bundle["itemIds"]) - 1
            }
        )

    if bundle_id in item.get("bundleIds", []):
        await DBHelper.update_document(
            "items",
            workspace_id,
            item_id,
            {"bundleIds": [b for b in item["bundleIds"] if b != bundle_id]}
        )

@router.delete("/{bundle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bundle(
    workspace_id: str,
    bundle_id: str,
    db = Depends(Database.get_db)
):
    """Delete a bundle."""
    # First remove this bundle ID from all items
    bundle = await DBHelper.find_document("bundles", workspace_id, bundle_id)
    if bundle:
        for item_id in bundle["itemIds"]:
            item = await DBHelper.find_document("items", workspace_id, item_id)
            if item and bundle_id in item.get("bundleIds", []):
                await DBHelper.update_document(
                    "items",
                    workspace_id,
                    item_id,
                    {"bundleIds": [b for b in item["bundleIds"] if b != bundle_id]}
                )

    # Then delete the bundle
    success = await DBHelper.delete_document("bundles", workspace_id, bundle_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Bundle not found"}}
        )