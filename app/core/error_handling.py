from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
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

def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with the FastAPI app."""
    
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        """Handle application-specific errors."""
        logger.error(f"Application error: {exc.message}", extra=exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "application_error",
                "message": exc.message,
                "details": exc.details
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred"
            }
        )