"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health check")
async def health_check() -> dict[str, str]:
    """Check if the service is running."""
    return {"status": "healthy"}
