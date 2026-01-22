"""
Cloud Connector Service - Handles OAuth flows for cloud providers
"""

import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.cloud_account import CloudAccount
from app.services.encryption_service import encryption_service


class CloudConnectorService:
    """Service for handling OAuth connections to cloud providers"""

    def __init__(self):
        # Google OAuth endpoints
        self.google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def generate_oauth_state(self, user_id: str) -> str:
        """
        Generate a secure state for OAuth flow that includes user_id
        Format: base64(user_id:random_token)
        """
        import base64
        state_data = f"{user_id}:{secrets.token_urlsafe(24)}"
        return base64.urlsafe_b64encode(state_data.encode()).decode()
    
    def extract_user_id_from_state(self, state: str) -> Optional[str]:
        """
        Extract user_id from OAuth state
        Returns None if state is invalid
        """
        try:
            import base64
            decoded = base64.urlsafe_b64decode(state.encode()).decode()
            user_id = decoded.split(":")[0]
            return user_id
        except Exception:
            return None

    def get_google_oauth_url(self, redirect_uri: str, state: str) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            redirect_uri: Redirect URI after OAuth
            state: OAuth state parameter
            
        Returns:
            OAuth authorization URL
        """
        if not settings.GOOGLE_CLIENT_ID:
            raise ValueError(
                "Google OAuth credentials not configured. "
                "Please set GOOGLE_CLIENT_ID in your environment variables."
            )

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.metadata.readonly https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
            "access_type": "offline",  # Required to get refresh token
            "prompt": "consent",  # Force consent to get refresh token
            "state": state,
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.google_auth_url}?{query_string}"

    async def exchange_google_code_for_tokens(
        self, code: str, redirect_uri: str
    ) -> dict:
        """
        Exchange Google OAuth code for access and refresh tokens
        
        Args:
            code: OAuth authorization code
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            {
                "access_token": "...",
                "refresh_token": "...",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
        """
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError(
                "Google OAuth credentials not configured. "
                "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your environment variables."
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.google_token_url,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_google_user_info(self, access_token: str) -> dict:
        """
        Get Google user information
        
        Args:
            access_token: Google access token
            
        Returns:
            {
                "id": "...",
                "email": "...",
                "name": "..."
            }
        """
        # Try userinfo v2 endpoint first
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.google_userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            # If v2 fails, try v1 endpoint
            if e.response.status_code == 401:
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            "https://www.googleapis.com/oauth2/v1/userinfo",
                            headers={"Authorization": f"Bearer {access_token}"},
                        )
                        response.raise_for_status()
                        return response.json()
                except Exception:
                    # If both fail, try using Google Drive API to get user info
                    try:
                        async with httpx.AsyncClient() as client:
                            # Use Drive API about endpoint to get user info
                            response = await client.get(
                                "https://www.googleapis.com/drive/v3/about",
                                headers={"Authorization": f"Bearer {access_token}"},
                                params={"fields": "user"}
                            )
                            response.raise_for_status()
                            data = response.json()
                            user_data = data.get("user", {})
                            return {
                                "id": user_data.get("permissionId"),
                                "email": user_data.get("emailAddress"),
                                "name": user_data.get("displayName"),
                            }
                    except Exception:
                        return {"id": None, "email": None, "name": None}
            raise

    async def create_or_update_cloud_account(
        self,
        db: AsyncSession,
        user_id: UUID,
        provider: str,
        access_token: str,
        refresh_token: Optional[str],
        expires_in: int,
        provider_account_id: Optional[str] = None,
    ) -> CloudAccount:
        """
        Create or update cloud account with encrypted tokens
        
        Args:
            db: Database session
            user_id: User ID
            provider: Provider name (google_drive, onedrive)
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expires_in: Token expiration in seconds
            provider_account_id: Provider's user ID (optional)
            
        Returns:
            CloudAccount instance
        """
        # Encrypt tokens using master key
        master_key = encryption_service.master_key
        access_token_encrypted = encryption_service.encrypt_token(access_token, master_key)
        refresh_token_encrypted = None
        if refresh_token:
            refresh_token_encrypted = encryption_service.encrypt_token(
                refresh_token, master_key
            )

        # Encode to base64 for storage
        access_token_encrypted_b64 = base64.b64encode(access_token_encrypted).decode(
            "utf-8"
        )
        refresh_token_encrypted_b64 = None
        if refresh_token_encrypted:
            refresh_token_encrypted_b64 = base64.b64encode(
                refresh_token_encrypted
            ).decode("utf-8")

        # Calculate expiration
        token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Check if account already exists
        result = await db.execute(
            select(CloudAccount).where(
                CloudAccount.user_id == user_id, CloudAccount.provider == provider
            )
        )
        existing_account = result.scalar_one_or_none()

        if existing_account:
            # Update existing account
            existing_account.access_token_encrypted = access_token_encrypted_b64
            existing_account.refresh_token_encrypted = refresh_token_encrypted_b64
            existing_account.token_expires_at = token_expires_at
            existing_account.provider_account_id = provider_account_id
            existing_account.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(existing_account)
            return existing_account
        else:
            # Create new account
            new_account = CloudAccount(
                user_id=user_id,
                provider=provider,
                provider_account_id=provider_account_id,
                access_token_encrypted=access_token_encrypted_b64,
                refresh_token_encrypted=refresh_token_encrypted_b64,
                token_expires_at=token_expires_at,
            )
            db.add(new_account)
            await db.commit()
            await db.refresh(new_account)
            return new_account


# Create singleton instance
cloud_connector_service = CloudConnectorService()
