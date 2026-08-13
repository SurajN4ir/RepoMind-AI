"""Shared HTTP exception mapping for application-layer errors."""

from fastapi import HTTPException, status

from app.application.exceptions import (
    ApplicationError,
    ConflictError,
    EntityNotFoundError,
    ExternalServiceError,
    ValidationError,
)


def to_http_exception(
    exc: ApplicationError, *, fallback_message: str = "Operation failed."
) -> HTTPException:
    """Map an application-layer exception to a stable FastAPI HTTP exception.

    Usage in route handlers::

        from app.application.http_exceptions import to_http_exception

        try:
            result = await service.perform(request)
        except ApplicationError as exc:
            raise to_http_exception(exc) from exc
    """
    if isinstance(exc, EntityNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    if isinstance(exc, ExternalServiceError):
        return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=fallback_message,
    )
