# Cloud Accounts API Contract v1.0.0

**Owner:** Bilal (Backend Infrastructure)  
**Version:** 1.0.0  
**Status:** 📝 Draft  
**Last Updated:** 2026-01-20  
**Dependencies:** 
- Backend API Contract v1.0.0
- Cloud Connector-Backend Contract v1.0.0

---

## Overview

This contract defines the Backend API endpoints for managing cloud storage accounts (Google Drive, OneDrive). These endpoints handle OAuth flows, account management, and cloud account status.

**Based on:** TASKS_PLANING.md - Day 2-4 tasks for Cloud Accounts

**Base URL:** `http://localhost:8000/api`

**Authentication:** Bearer token in `Authorization` header (required for all endpoints)

---

## Endpoints

### GET /api/cloud-accounts

List all cloud accounts for the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "accounts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "provider": "google_drive",
      "provider_account_id": "user123@gmail.com",
      "is_connected": true,
      "token_expires_at": "2026-01-21T10:00:00Z",
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:00:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "provider": "onedrive",
      "provider_account_id": "user123@outlook.com",
      "is_connected": true,
      "token_expires_at": "2026-01-21T11:00:00Z",
      "created_at": "2026-01-20T11:00:00Z",
      "updated_at": "2026-01-20T11:00:00Z"
    }
  ],
  "total": 2
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

**Mock Response:**
```json
{
  "accounts": [
    {
      "id": "mock-account-id-1",
      "provider": "google_drive",
      "provider_account_id": "mock@gmail.com",
      "is_connected": true,
      "token_expires_at": "2026-01-21T10:00:00Z",
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### POST /api/cloud-accounts/connect/{provider}

Initiate OAuth flow for connecting a cloud account.

**Path Parameters:**
- `provider`: `google_drive` or `onedrive`

**Query Parameters:**
- `redirect_uri` (required): Frontend callback URL after OAuth

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&response_type=code&scope=...&state=...",
  "state": "random_state_string_for_verification"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid provider or missing redirect_uri
- `401 Unauthorized`: Invalid or missing token
- `409 Conflict`: Account already connected for this provider

**Mock Response:**
```json
{
  "oauth_url": "https://mock-oauth-provider.com/auth?state=mock_state",
  "state": "mock_state_12345"
}
```

---

### GET /api/cloud-accounts/callback/{provider}

Handle OAuth callback after user authorization.

**Path Parameters:**
- `provider`: `google_drive` or `onedrive`

**Query Parameters:**
- `code` (required): Authorization code from OAuth provider
- `state` (required): State parameter for verification
- `error` (optional): Error code if authorization failed

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider": "google_drive",
  "provider_account_id": "user123@gmail.com",
  "is_connected": true,
  "message": "Account connected successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid code, state mismatch, or missing parameters
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: OAuth exchange failed

**Mock Response:**
```json
{
  "account_id": "mock-account-id-1",
  "provider": "google_drive",
  "provider_account_id": "mock@gmail.com",
  "is_connected": true,
  "message": "Account connected successfully"
}
```

---

### DELETE /api/cloud-accounts/{account_id}

Disconnect a cloud account.

**Path Parameters:**
- `account_id`: UUID of the cloud account

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Account disconnected successfully",
  "account_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Account not found or doesn't belong to user
- `500 Internal Server Error`: Failed to disconnect account

**Mock Response:**
```json
{
  "message": "Account disconnected successfully",
  "account_id": "mock-account-id-1"
}
```

---

### POST /api/cloud-accounts/{account_id}/refresh

Manually refresh access token for a cloud account.

**Path Parameters:**
- `account_id`: UUID of the cloud account

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Token refreshed successfully",
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "token_expires_at": "2026-01-21T12:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Account not found or doesn't belong to user
- `400 Bad Request`: Refresh token expired, re-authentication required
- `500 Internal Server Error`: Token refresh failed

**Mock Response:**
```json
{
  "message": "Token refreshed successfully",
  "account_id": "mock-account-id-1",
  "token_expires_at": "2026-01-21T12:00:00Z"
}
```

---

### GET /api/cloud-accounts/{account_id}/status

Check connection status of a cloud account.

**Path Parameters:**
- `account_id`: UUID of the cloud account

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider": "google_drive",
  "is_connected": true,
  "token_expires_at": "2026-01-21T10:00:00Z",
  "token_expires_in_seconds": 3600,
  "last_sync_at": "2026-01-20T10:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: Account not found or doesn't belong to user

**Mock Response:**
```json
{
  "account_id": "mock-account-id-1",
  "provider": "google_drive",
  "is_connected": true,
  "token_expires_at": "2026-01-21T10:00:00Z",
  "token_expires_in_seconds": 3600,
  "last_sync_at": "2026-01-20T10:00:00Z"
}
```

---

## Data Schemas

### CloudAccountResponse
```typescript
{
  id: string (UUID)
  provider: "google_drive" | "onedrive"
  provider_account_id: string
  is_connected: boolean
  token_expires_at: string (ISO 8601 datetime) | null
  created_at: string (ISO 8601 datetime)
  updated_at: string (ISO 8601 datetime)
}
```

### CloudAccountListResponse
```typescript
{
  accounts: CloudAccountResponse[]
  total: number
}
```

### OAuthInitiateResponse
```typescript
{
  oauth_url: string
  state: string
}
```

### OAuthCallbackResponse
```typescript
{
  account_id: string (UUID)
  provider: "google_drive" | "onedrive"
  provider_account_id: string
  is_connected: boolean
  message: string
}
```

---

## Provider Values

**Supported Providers:**
- `google_drive` - Google Drive
- `onedrive` - Microsoft OneDrive

**Future Providers:**
- `dropbox` - Dropbox (not in MVP)
- `box` - Box (not in MVP)

---

## OAuth Flow Details

### Frontend Flow

1. **User clicks "Connect Google Drive"**
   - Frontend calls `POST /api/cloud-accounts/connect/google_drive?redirect_uri=...`
   - Backend returns `oauth_url` and `state`
   - Frontend stores `state` in session/localStorage
   - Frontend redirects user to `oauth_url`

2. **User authorizes on provider site**
   - Provider redirects to `redirect_uri` with `code` and `state`
   - Frontend extracts `code` and `state` from URL

3. **Frontend calls callback endpoint**
   - Frontend calls `GET /api/cloud-accounts/callback/google_drive?code=...&state=...`
   - Backend exchanges code for tokens and stores account
   - Backend returns account details
   - Frontend updates UI to show connected account

### Backend Flow

1. **Generate OAuth URL**
   - Validate provider
   - Generate random `state` parameter
   - Store `state` in session/cache (for verification)
   - Call cloud connector service to generate OAuth URL
   - Return OAuth URL and state

2. **Handle OAuth Callback**
   - Verify `state` parameter matches stored value
   - Extract `code` from query parameters
   - Call cloud connector service to exchange code for tokens
   - Encrypt tokens using encryption service
   - Create/update CloudAccount record in database
   - Return account details

---

## Error Handling

### Common Error Codes

- `400 Bad Request`: Invalid input, missing parameters, or business logic error
- `401 Unauthorized`: Authentication required or failed
- `404 Not Found`: Resource not found
- `409 Conflict`: Account already connected for provider
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Change Log

### v1.0.0 (2026-01-20) - Initial Draft
- Cloud accounts list endpoint
- OAuth initiation endpoint
- OAuth callback endpoint
- Account disconnect endpoint
- Token refresh endpoint
- Account status endpoint

---

## Implementation Tasks (from TASKS_PLANING.md)

### Day 2: Core Backend Features
- [ ] Create CloudAccount model
- [ ] Create cloud accounts API routes
- [ ] Implement OAuth initiation
- [ ] Implement OAuth callback handling

### Day 4: Cloud Account Management
- [ ] Implement account linking/unlinking
- [ ] Add account status checks
- [ ] Implement token refresh on expiry
- [ ] Add error handling for OAuth failures
- [ ] Test account management
- [ ] Add account validation

---

**Contract Owner:** Bilal (Backend Infrastructure)  
**Status:** Draft - Implementation in progress per TASKS_PLANING.md
