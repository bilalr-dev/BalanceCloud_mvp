"""
BalanceCloud MVP - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import auth, files

# Note: Database tables are created via Alembic migrations
# Run: alembic upgrade head

app = FastAPI(
    title="BalanceCloud MVP API",
    description="Simplified Zero-Trust File Storage - MVP Version",
    version="0.1.0-mvp",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(files.router, prefix="/api/files", tags=["files"])


@app.on_event("startup")
async def startup_event():
    # Database tables are created via Alembic migrations
    # Run: alembic upgrade head
    pass


@app.get("/")
async def root():
    return {
        "message": "BalanceCloud MVP API",
        "version": "0.1.0-mvp",
        "description": "Simplified version - local storage only",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
