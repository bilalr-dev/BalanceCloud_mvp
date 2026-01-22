"""
Cloud Account Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CloudAccountResponse(BaseModel):
    """Cloud account response schema"""

    id: str
    provider: str = Field(..., description="Provider: google_drive or onedrive")
    provider_account_id: Optional[str] = None
    is_connected: bool = Field(default=True, description="Whether account is connected")
    token_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CloudAccountListResponse(BaseModel):
    """List of cloud accounts response"""

    accounts: list[CloudAccountResponse]
    total: int


class OAuthInitiateResponse(BaseModel):
    """OAuth initiation response"""

    oauth_url: str = Field(..., description="URL to redirect user for OAuth")
    state: str = Field(..., description="OAuth state parameter for verification")


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response"""

    account_id: str
    provider: str
    provider_account_id: str
    is_connected: bool
    message: str
