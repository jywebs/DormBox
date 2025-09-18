"""Routes package."""
from fastapi import APIRouter

from .boxes import router as boxes_router
from .items import router as items_router
from .bundles import router as bundles_router

# Create a main router to include all sub-routers
router = APIRouter()

# Include sub-routers with their prefixes
router.include_router(boxes_router, prefix="/boxes", tags=["boxes"])
router.include_router(items_router, prefix="/items", tags=["items"])
router.include_router(bundles_router, prefix="/bundles", tags=["bundles"])