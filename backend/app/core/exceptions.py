"""Custom exception helpers for PulseML."""

from fastapi import HTTPException, status


class PulseMLHTTPException(HTTPException):
    """Base HTTP exception that keeps responses consistent."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(status_code=status_code, detail={"message": detail})


def not_found(resource: str) -> PulseMLHTTPException:
    """Return a standardized not found exception."""

    return PulseMLHTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found"
    )


def unauthorized(detail: str = "Not authenticated") -> PulseMLHTTPException:
    """Return an unauthorized HTTP exception."""

    return PulseMLHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


def forbidden(detail: str = "Insufficient permissions") -> PulseMLHTTPException:
    """Return a forbidden HTTP exception."""

    return PulseMLHTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )

