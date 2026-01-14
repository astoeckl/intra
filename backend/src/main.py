from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.database import init_db
from src.api.routes import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CRM/Intranet System for Lead-Management and Customer Care",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Atikon CRM/Intranet API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled",
    }
