from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Type, Callable, Union
import logging

# Get logger
logger = logging.getLogger(__name__)

class ApplicationError(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(ApplicationError):
    """Validation error exception."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=400, details=details)

class ProcessingError(ApplicationError):
    """Processing error exception."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=500, details=details)

class ResourceNotFoundError(ApplicationError):
    """Resource not found exception."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, status_code=404, details=details)

# Exception handler mapping
exception_handlers: Dict[Type[Exception], Callable] = {}

def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with the FastAPI application."""
    
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        """Handle application errors."""
        logger.error(f"Application error: {exc.message}", extra=exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred"
            }
        )