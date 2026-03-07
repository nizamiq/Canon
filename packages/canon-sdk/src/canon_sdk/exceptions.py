"""
Canon SDK Exceptions

Custom exception types for Canon SDK error handling.
"""


class CanonError(Exception):
    """Base exception for all Canon SDK errors."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CanonAPIError(CanonError):
    """Raised when the Canon API returns an error response."""
    
    def __init__(self, message: str, status_code: int | None = None, response_body: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class CanonAuthError(CanonAPIError):
    """Raised when authentication fails (401/403 responses)."""
    pass


class CanonNotFoundError(CanonAPIError):
    """Raised when a requested prompt is not found (404 response)."""
    pass


class CanonValidationError(CanonAPIError):
    """Raised when request validation fails (422 response)."""
    pass


class CanonTimeoutError(CanonError):
    """Raised when a request times out."""
    pass


class CanonConnectionError(CanonError):
    """Raised when connection to Canon service fails."""
    pass
