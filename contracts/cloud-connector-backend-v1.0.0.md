# Cloud Connector-Backend Contract v1.0.0

**Owner:** Helijao (Cloud Connectors)  
**Version:** 1.0.0  
**Status:** 📝 Draft  
**Last Updated:** 2026-01-20  
**Dependencies:** 
- Backend API Contract v1.0.0
- Encryption Service Contract v1.0.0 (for chunk encryption)

---

## Overview

This contract defines the interface between Cloud Connector services (Google Drive, OneDrive) and the Backend. It specifies OAuth flows, token management, and cloud storage operations.

**Based on:** TASKS_PLANING.md - Day 1-4 tasks for Cloud Connectors

---

## OAuth2 Flow

### Google Drive OAuth

**Step 1: Initiate OAuth**
- Frontend redirects user to backend endpoint
- Backend generates OAuth URL and redirects to Google
- User authorizes application

**Step 2: OAuth Callback**
- Google redirects to backend callback endpoint with authorization code
- Backend exchanges code for access token and refresh token
- Backend stores encrypted tokens in database (CloudAccount model)

**Step 3: Token Refresh**
- Backend automatically refreshes tokens when expired
- Uses refresh token to get new access token
- Updates encrypted tokens in database

### OneDrive OAuth

**Step 1: Initiate OAuth**
- Frontend redirects user to backend endpoint
- Backend generates OAuth URL and redirects to Microsoft
- User authorizes application

**Step 2: OAuth Callback**
- Microsoft redirects to backend callback endpoint with authorization code
- Backend exchanges code for access token and refresh token
- Backend stores encrypted tokens in database (CloudAccount model)

**Step 3: Token Refresh**
- Backend automatically refreshes tokens when expired
- Uses refresh token to get new access token
- Updates encrypted tokens in database

---

## Cloud Connector Service Interface

### Methods Required

```python
class CloudConnectorService:
    """Interface for cloud connector implementations"""
    
    async def get_oauth_url(self, user_id: str, redirect_uri: str) -> str:
        """Generate OAuth authorization URL"""
        pass
    
    async def handle_oauth_callback(
        self, 
        code: str, 
        state: str, 
        redirect_uri: str
    ) -> dict:
        """Exchange authorization code for tokens"""
        # Returns: {
        #   "access_token": "...",
        #   "refresh_token": "...",
        #   "expires_in": 3600,
        #   "provider_account_id": "..."
        # }
        pass
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        # Returns: {
        #   "access_token": "...",
        #   "refresh_token": "...",
        #   "expires_in": 3600
        # }
        pass
    
    async def upload_file(
        self,
        access_token: str,
        file_path: str,
        file_data: bytes,
        mime_type: str
    ) -> dict:
        """Upload file to cloud storage"""
        # Returns: {
        #   "cloud_file_id": "...",
        #   "file_size": 1024,
        #   "uploaded_at": "2026-01-20T10:00:00Z"
        # }
        pass
    
    async def download_file(
        self,
        access_token: str,
        cloud_file_id: str
    ) -> bytes:
        """Download file from cloud storage"""
        # Returns: file data as bytes
        pass
    
    async def delete_file(
        self,
        access_token: str,
        cloud_file_id: str
    ) -> bool:
        """Delete file from cloud storage"""
        # Returns: True if successful
        pass
    
    async def list_files(
        self,
        access_token: str,
        folder_id: str = None
    ) -> list:
        """List files in cloud storage"""
        # Returns: [
        #   {
        #     "cloud_file_id": "...",
        #     "name": "...",
        #     "size": 1024,
        #     "mime_type": "...",
        #     "is_folder": False
        #   }
        # ]
        pass
```

---

## Provider-Specific Requirements

### Google Drive

**OAuth Scopes Required:**
- `https://www.googleapis.com/auth/drive.file` - Access to files created by app
- `https://www.googleapis.com/auth/drive.readonly` - Read-only access

**API Endpoints:**
- Authorization: `https://accounts.google.com/o/oauth2/v2/auth`
- Token: `https://oauth2.googleapis.com/token`
- Upload: `https://www.googleapis.com/upload/drive/v3/files`
- Download: `https://www.googleapis.com/drive/v3/files/{fileId}?alt=media`

**Library:** `google-api-python-client`

### OneDrive

**OAuth Scopes Required:**
- `Files.ReadWrite` - Read and write user files
- `offline_access` - Access token refresh

**API Endpoints:**
- Authorization: `https://login.microsoftonline.com/common/oauth2/v2.0/authorize`
- Token: `https://login.microsoftonline.com/common/oauth2/v2.0/token`
- Upload: `https://graph.microsoft.com/v1.0/me/drive/items/{itemId}/content`
- Download: `https://graph.microsoft.com/v1.0/me/drive/items/{itemId}/content`

**Library:** `msal` (Microsoft Authentication Library)

---

## Error Handling

### OAuth Errors
- `INVALID_GRANT`: Refresh token expired or invalid → Re-authenticate
- `INVALID_CLIENT`: OAuth credentials invalid → Check configuration
- `ACCESS_DENIED`: User denied authorization → Show error message

### API Errors
- `401 Unauthorized`: Token expired → Refresh token automatically
- `403 Forbidden`: Insufficient permissions → Request additional scopes
- `404 Not Found`: File not found → Handle gracefully
- `429 Too Many Requests`: Rate limited → Implement backoff

---

## Token Storage

**Database Model:** `CloudAccount`
- `access_token_encrypted`: Encrypted access token (AES-256-GCM)
- `refresh_token_encrypted`: Encrypted refresh token (AES-256-GCM)
- `token_expires_at`: Token expiration timestamp
- `provider_account_id`: Cloud provider's user ID

**Encryption:**
- Use application master key (ENCRYPTION_KEY) to encrypt tokens
- Tokens must be encrypted at rest
- Decrypt only when needed for API calls

---

## Integration Points

### With Backend API Routes
- `POST /api/cloud-accounts/connect/{provider}` - Initiate OAuth
- `GET /api/cloud-accounts/callback/{provider}` - Handle OAuth callback
- `POST /api/cloud-accounts/{account_id}/refresh` - Manual token refresh

### With Cloud Upload Service
- Cloud connector provides upload/download methods
- Upload service calls connector methods
- Handles chunk uploads (multiple API calls for large files)

### With Cloud Download Service
- Cloud connector provides download methods
- Download service calls connector methods
- Handles chunk downloads and reassembly

---

## Mock Implementation

**For Frontend Development:**
```typescript
// Mock OAuth flow
const mockOAuthUrl = 'https://mock-oauth-provider.com/auth'
const mockTokens = {
  access_token: 'mock_access_token',
  refresh_token: 'mock_refresh_token',
  expires_in: 3600
}
```

**For Backend Testing:**
```python
# Mock cloud connector service
class MockCloudConnectorService:
    async def upload_file(self, access_token, file_path, file_data, mime_type):
        return {
            "cloud_file_id": "mock_file_id_123",
            "file_size": len(file_data),
            "uploaded_at": "2026-01-20T10:00:00Z"
        }
```

---

## Change Log

### v1.0.0 (2026-01-20) - Initial Draft
- OAuth2 flow defined for Google Drive and OneDrive
- Cloud connector service interface defined
- Token storage requirements specified
- Error handling patterns defined

---

## Implementation Tasks (from TASKS_PLANING.md)

### Day 1: OAuth Setup & Research
- [ ] Research Google Drive OAuth2 flow
- [ ] Research OneDrive OAuth2 flow
- [ ] Set up OAuth credentials in Google Cloud Console
- [ ] Set up OAuth credentials in Azure Portal
- [ ] Create `cloud_connector_service.py` skeleton
- [ ] Test OAuth redirect URLs

### Day 2: Google Drive Integration
- [ ] Implement Google Drive OAuth2 flow
- [ ] Create `cloud_connector_service.py` for Google
- [ ] Implement token refresh logic
- [ ] Test Google Drive connection
- [ ] Create basic upload to Google Drive
- [ ] Create basic download from Google Drive

### Day 3: OneDrive Integration
- [ ] Implement OneDrive OAuth2 flow
- [ ] Add OneDrive to cloud connector service
- [ ] Implement OneDrive upload
- [ ] Implement OneDrive download
- [ ] Test OneDrive connection
- [ ] Handle token refresh

### Day 4: Cloud Account Management
- [ ] Implement account linking/unlinking
- [ ] Add account status checks
- [ ] Implement token refresh on expiry
- [ ] Add error handling for OAuth failures
- [ ] Test account management
- [ ] Add account validation

---

**Contract Owner:** Helijao  
**Status:** Draft - Implementation in progress per TASKS_PLANING.md
