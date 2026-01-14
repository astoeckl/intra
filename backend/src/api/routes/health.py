from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.database import get_db

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "Atikon CRM/Intranet API"}


@router.get("/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Database connectivity health check."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
