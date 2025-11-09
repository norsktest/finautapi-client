"""Exception classes for the FinAut API client."""


class FinAutAPIException(Exception):
    """Base exception for all FinAut API errors."""

    def __init__(self, message, response=None, status_code=None):
        super().__init__(message)
        self.message = message
        self.response = response
        self.status_code = status_code


class AuthenticationError(FinAutAPIException):
    """Raised when authentication fails."""
    pass


class ValidationError(FinAutAPIException):
    """Raised when request validation fails."""
    pass


class NotFoundError(FinAutAPIException):
    """Raised when a resource is not found."""
    pass


class PermissionDeniedError(FinAutAPIException):
    """Raised when access is denied to a resource."""
    pass


class ServerError(FinAutAPIException):
    """Raised when the server returns a 5xx error."""
    pass


class RateLimitError(FinAutAPIException):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message, response=None, retry_after=None):
        super().__init__(message, response)
        self.retry_after = retry_after


class WebhookError(FinAutAPIException):
    """Raised when webhook operations fail."""
    pass


class ConnectionError(FinAutAPIException):
    """Raised when connection to the API fails."""
    pass