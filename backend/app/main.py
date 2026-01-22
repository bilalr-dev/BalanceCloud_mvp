"""
BalanceCloud MVP - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional

from typing import Optional

from fastapi import Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import auth, cloud_accounts, files
from app.api.routes.auth import get_current_user
from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.models.user import User
from app.schemas.cloud_account import CloudAccountResponse

# Note: Database tables are created via Alembic migrations
# Run: alembic upgrade head

app = FastAPI(
    title="BalanceCloud MVP API",
    description="Simplified Zero-Trust File Storage - MVP Version",
    version="0.1.0-mvp",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Security headers middleware (add first to ensure headers on all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware (Redis-based)
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitingMiddleware,
        requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=[
        "Content-Disposition",
        "Content-Length",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(
    cloud_accounts.router, prefix="/api/cloud-accounts", tags=["cloud-accounts"]
)

# Add alias route for Google OAuth callback (matches user's configured redirect URI)
# This allows the callback to work with the redirect URI: http://localhost:8000/api/auth/google/callback
from app.api.routes.cloud_accounts import oauth_callback


@app.get("/api/auth/google/callback")
async def google_oauth_callback_alias(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Google OAuth callback endpoint (alias for /api/cloud-accounts/callback/google_drive)
    This matches the redirect URI configured in Google Cloud Console: http://localhost:8000/api/auth/google/callback
    Note: This endpoint does not require authentication as Google redirects here without auth headers
    """
    # Delegate to the cloud_accounts callback handler
    return await oauth_callback(
        provider="google_drive",
        code=code,
        state=state,
        error=error,
        db=db,
    )


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
