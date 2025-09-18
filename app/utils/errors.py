"""Error handling utilities."""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class AppError(Exception):
    """Base application error."""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

class NotFoundError(AppError):
    """Resource not found error."""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="not_found",
            message=f"{resource} with id {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class ValidationError(AppError):
    """Validation error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="validation_error",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

class AccessDeniedError(AppError):
    """Access denied error."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            code="access_denied",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

def bad_request(message: str, code: str = "bad_request") -> HTTPException:
    """Create a bad request error."""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": {"code": code, "message": message}}
    )

def not_found(resource: str, resource_id: str) -> HTTPException:
    """Create a not found error."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": {"code": "not_found", "message": f"{resource} with id {resource_id} not found"}}
    )

def internal_error(message: str = "An internal server error occurred") -> HTTPException:
    """Create an internal server error."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"error": {"code": "internal_error", "message": message}}
    )