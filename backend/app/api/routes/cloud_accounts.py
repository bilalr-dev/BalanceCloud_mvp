"""
Cloud Accounts API Routes
Basic implementation for MVP - returns empty list until OAuth is configured
"""

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.cloud_account import (
    CloudAccountListResponse,
    CloudAccountResponse,
    OAuthInitiateResponse,
)

router = APIRouter()


@router.get("", response_model=CloudAccountListResponse)
async def list_cloud_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all cloud accounts for the current user.
    
    Returns empty list until OAuth credentials are configured.
    """
    # TODO: Implement when cloud connector service is ready
    # For now, return empty list so frontend doesn't break
    return CloudAccountListResponse(accounts=[], total=0)


@router.post(
    "/connect/{provider}",
    response_model=OAuthInitiateResponse,
    status_code=status.HTTP_200_OK,
)
async def initiate_oauth(
    provider: str,
    redirect_uri: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate OAuth flow for connecting a cloud account.
    
    Returns a placeholder response until OAuth credentials are configured.
    """
    if provider not in ["google_drive", "onedrive"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}. Supported: google_drive, onedrive",
        )

    # TODO: Implement OAuth flow when cloud connector service is ready
    # For now, return a placeholder that indicates OAuth is not configured
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"OAuth for {provider} is not yet configured. Please configure OAuth credentials in Google Cloud Console / Azure Portal first.",
    )


@router.get("/callback/{provider}", response_model=CloudAccountResponse)
async def oauth_callback(
    provider: str,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback from cloud provider.
    
    Returns a placeholder response until OAuth credentials are configured.
    """
    if provider not in ["google_drive", "onedrive"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}",
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}",
        )

    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing OAuth parameters: code and state are required",
        )

    # TODO: Implement OAuth callback handling when cloud connector service is ready
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"OAuth callback for {provider} is not yet configured. Please configure OAuth credentials first.",
    )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_cloud_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disconnect a cloud account.
    
    Returns success even if account doesn't exist (idempotent).
    """
    # TODO: Implement when cloud connector service is ready
    # For now, return success so frontend doesn't break
    return None


@router.post("/{account_id}/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh OAuth token for a cloud account.
    
    Returns success even if account doesn't exist.
    """
    # TODO: Implement when cloud connector service is ready
    # For now, return success so frontend doesn't break
    return {"message": "Token refresh not yet implemented"}
