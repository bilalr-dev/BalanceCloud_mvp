"""
Cloud Accounts API Routes
Handles OAuth flows for connecting cloud storage accounts
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.cloud_account import CloudAccount
from app.models.user import User
from app.schemas.cloud_account import (
    CloudAccountListResponse,
    CloudAccountResponse,
    OAuthInitiateResponse,
)
from app.services.cloud_connector_service import cloud_connector_service
from app.services.encryption_service import encryption_service

router = APIRouter()


@router.get("", response_model=CloudAccountListResponse)
async def list_cloud_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all cloud accounts for the current user.
    """
    try:
        result = await db.execute(
            select(CloudAccount).where(CloudAccount.user_id == current_user.id)
        )
        accounts = result.scalars().all()

        account_responses = []
        for account in accounts:
            # Check if token is expired
            is_connected = True
            if account.token_expires_at:
                from datetime import datetime

                is_connected = account.token_expires_at > datetime.utcnow()

            account_responses.append(
                CloudAccountResponse(
                    id=str(account.id),
                    provider=account.provider,
                    provider_account_id=account.provider_account_id,
                    is_connected=is_connected,
                    token_expires_at=account.token_expires_at,
                    created_at=account.created_at,
                    updated_at=account.updated_at,
                )
            )

        return CloudAccountListResponse(accounts=account_responses, total=len(account_responses))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list cloud accounts: {str(e)}",
        )


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
    """
    if provider not in ["google_drive", "onedrive"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}. Supported: google_drive, onedrive",
        )

    try:
        # Always use the redirect_uri from settings (must match Google Console configuration)
        # The redirect_uri parameter from frontend is ignored to ensure it matches Google Console
        if provider == "google_drive":
            if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth credentials not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment variables.",
                )
            if not settings.GOOGLE_REDIRECT_URI:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="GOOGLE_REDIRECT_URI not configured. Please set it in your .env file to match Google Console configuration.",
                )
            # Always use the redirect URI from settings (must match Google Console)
            final_redirect_uri = settings.GOOGLE_REDIRECT_URI
        else:
            # OneDrive not implemented yet
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="OneDrive OAuth is not yet implemented.",
            )

        # Generate state for OAuth flow (includes user_id for callback)
        state = cloud_connector_service.generate_oauth_state(str(current_user.id))

        # Store state in session/database for verification (simplified - store in memory for now)
        # In production, use Redis or database to store state
        if provider == "google_drive":
            oauth_url = cloud_connector_service.get_google_oauth_url(
                final_redirect_uri, state
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"OAuth for {provider} is not yet implemented.",
            )

        return OAuthInitiateResponse(oauth_url=oauth_url, state=state)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}",
        )


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback from cloud provider.
    """
    if provider not in ["google_drive", "onedrive"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}",
        )

    if error:
        # Redirect to frontend with error
        frontend_url = settings.CORS_ORIGINS.split(",")[0].strip() if settings.CORS_ORIGINS else "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/cloud-accounts?error={error}",
            status_code=status.HTTP_302_FOUND
        )

    if not code:
        # Redirect to frontend with error
        frontend_url = settings.CORS_ORIGINS.split(",")[0].strip() if settings.CORS_ORIGINS else "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/cloud-accounts?error=missing_code",
            status_code=status.HTTP_302_FOUND
        )

    # Extract user_id from state (state contains user_id:random_token)
    if not state:
        frontend_url = settings.CORS_ORIGINS.split(",")[0].strip() if settings.CORS_ORIGINS else "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/cloud-accounts?error=missing_state",
            status_code=status.HTTP_302_FOUND
        )
    
    user_id = cloud_connector_service.extract_user_id_from_state(state)
    if not user_id:
        frontend_url = settings.CORS_ORIGINS.split(",")[0].strip() if settings.CORS_ORIGINS else "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/cloud-accounts?error=invalid_state",
            status_code=status.HTTP_302_FOUND
        )
    
    # Get user from database
    from sqlalchemy import select
    from app.models.user import User
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        frontend_url = settings.CORS_ORIGINS.split(",")[0].strip() if settings.CORS_ORIGINS else "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/cloud-accounts?error=user_not_found",
            status_code=status.HTTP_302_FOUND
        )

    try:
        if provider == "google_drive":
            if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                frontend_url = settings.CORS_ORIGINS.split(",")[0].strip() if settings.CORS_ORIGINS else "http://localhost:5173"
                return RedirectResponse(
                    url=f"{frontend_url}/cloud-accounts?error=oauth_not_configured",
                    status_code=status.HTTP_302_FOUND
                )

            # Use the configured redirect URI
            redirect_uri = settings.GOOGLE_REDIRECT_URI

            # Exchange code for tokens
            tokens = await cloud_connector_service.exchange_google_code_for_tokens(
                code, redirect_uri
            )

            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
            expires_in = tokens.get("expires_in", 3600)

            if not access_token:
                frontend_url = settings.CORS_ORIGINS.split(",")[0].strip() if settings.CORS_ORIGINS else "http://localhost:5173"
                return RedirectResponse(
                    url=f"{frontend_url}/cloud-accounts?error=token_exchange_failed",
                    status_code=status.HTTP_302_FOUND
                )

            # Get user info to get provider_account_id (email or name preferred)
            try:
                user_info = await cloud_connector_service.get_google_user_info(access_token)
                # Prefer email, then name, then id, finally fallback
                provider_account_id = (
                    user_info.get("email") 
                    or user_info.get("name") 
                    or user_info.get("emailAddress")  # From Drive API
                    or user_info.get("displayName")   # From Drive API
                    or user_info.get("id")
                    or f"google_user_{user.id}"
                )
            except Exception as e:
                # If userinfo fails, use a placeholder based on user ID
                # Log the error for debugging
                import logging
                logging.error(f"Failed to get Google user info: {e}")
                provider_account_id = f"google_user_{user.id}"

            # Create or update cloud account
            cloud_account = await cloud_connector_service.create_or_update_cloud_account(
                db=db,
                user_id=user.id,
                provider="google_drive",
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                provider_account_id=provider_account_id,
            )

            # Redirect to frontend cloud accounts page after successful OAuth
            # Frontend will automatically refresh the accounts list
            frontend_url = settings.CORS_ORIGINS.split(",")[0].strip() if settings.CORS_ORIGINS else "http://localhost:5173"
            return RedirectResponse(
                url=f"{frontend_url}/cloud-accounts?connected=google_drive",
                status_code=status.HTTP_302_FOUND
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"OAuth callback for {provider} is not yet implemented.",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete OAuth flow: {str(e)}",
        )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_cloud_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disconnect a cloud account.
    """
    try:
        account_uuid = UUID(account_id)
        result = await db.execute(
            select(CloudAccount).where(
                CloudAccount.id == account_uuid,
                CloudAccount.user_id == current_user.id,
            )
        )
        account = result.scalar_one_or_none()

        if account:
            await db.delete(account)
            await db.commit()

        return None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect account: {str(e)}",
        )


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
