"""Main FastAPI application module."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings, init_indexes, Database
from app.routes import router

# Create FastAPI app
app = FastAPI(
    title=get_settings().app_name,
    description="API for tracking college move-in boxes and items",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add main router
app.include_router(router, prefix=get_settings().api_prefix)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    await init_indexes()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await Database.close_db()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An internal server error occurred"
            }
        }
    )