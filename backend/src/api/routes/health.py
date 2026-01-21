"""
Health Check API Routes.

Provides liveness and readiness probes for monitoring and orchestration.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.database import get_db

router = APIRouter()


@router.get("")
async def health_check():
    """
    Basic liveness probe.

    Returns:
        Service name and healthy status.
    """
    return {"status": "healthy", "service": "Atikon CRM/Intranet API"}


@router.get("/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """
    Database connectivity readiness probe.

    Verifies database connection is alive and responsive.

    Returns:
        Healthy status on success, unhealthy with error details on failure.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
