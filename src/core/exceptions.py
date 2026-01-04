from typing import Any, Dict, Optional

class AppException(Exception):
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        err_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.err_code = err_code
        self.details = details or {}
        super().__init__(self.message)

class EntityNotFoundError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, err_code="NOT_FOUND", details=details)

class ExternalServiceError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=502, err_code="BAD_GATEWAY", details=details)
