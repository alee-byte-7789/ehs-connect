"""
Service-layer exceptions.

Services raise these instead of FastAPI's HTTPException so the service
layer stays framework-agnostic (testable without spinning up FastAPI, and
reusable if a second interface — e.g. a CLI or admin script — is added
later). The API layer (app/api) catches these and maps them to HTTP
responses.
"""


class ServiceError(Exception):
    """Base class for all service-layer errors."""


class ConflictError(ServiceError):
    """Requested state already exists (duplicate registration, etc.)."""


class NotFoundError(ServiceError):
    """Requested entity does not exist."""


class AuthenticationError(ServiceError):
    """Invalid credentials, or account not in a loggable-in state."""


class AuthorizationError(ServiceError):
    """Authenticated, but not permitted to perform this action."""


class InvalidStateError(ServiceError):
    """Action is not valid given the entity's current state (e.g. already approved)."""
