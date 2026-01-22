# Backend API Contract v1.0.0

**Owner:** Dev 1 (Backend Infrastructure)  
**Version:** 1.0.0  
**Status:** ✅ Stable  
**Last Updated:** 2026-01-22  
**Dependencies:** None

---

## Overview

This contract defines the Backend API interface for the BalanceCloud MVP. All endpoints, request/response schemas, and behaviors are guaranteed to remain stable.

**Base URL:** `http://localhost:8000/api`

**Authentication:** Bearer token in `Authorization` header

---

## Endpoints

### POST /api/auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `400 Bad Request`: Email already exists or invalid input
- `422 Unprocessable Entity`: Validation error

**Mock Response:**
```json
{
  "access_token": "mock_token_register_12345",
  "token_type": "bearer"
}
```

---

### POST /api/auth/login

Authenticate user and get access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Incorrect email or password

**Mock Response:**
```json
{
  "access_token": "mock_token_login_12345",
  "token_type": "bearer"
}
```

---

### GET /api/auth/me

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-01-20T10:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token

**Mock Response:**
```json
{
  "id": "mock-user-id-12345",
  "email": "mock@example.com",
  "is_active": true,
  "created_at": "2026-01-20T10:00:00Z"
}
```

---

### GET /api/files

List files for the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `parent_id` (optional): Filter by parent folder ID

**Response (200 OK):**
```json
{
  "files": [
    {
      "id": "file-id-123",
      "user_id": "user-id-123",
      "name": "document.pdf",
      "path": "/documents/document.pdf",
      "size": 1024,
      "mime_type": "application/pdf",
      "is_folder": false,
      "parent_id": null,
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Mock Response:**
```json
{
  "files": [
    {
      "id": "mock-file-id-1",
      "user_id": "mock-user-id",
      "name": "Mock Document.pdf",
      "path": "/mock/document.pdf",
      "size": 2048,
      "mime_type": "application/pdf",
      "is_folder": false,
      "parent_id": null,
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### GET /api/files/storage/usage

Get storage usage for the current user, including local storage quota and cloud storage usage.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "used_bytes": 127682,
  "total_bytes": 10737418240,
  "used_percentage": 0.0,
  "used_gb": 0.0,
  "total_gb": 10.0,
  "cloud_storage": {
    "google_drive": {
      "used_bytes": 5368709120,
      "total_bytes": 16106127360,
      "used_percentage": 33.33,
      "used_gb": 5.0,
      "total_gb": 15.0
    } | null,
    "onedrive": {
      "used_bytes": 2147483648,
      "total_bytes": 5368709120,
      "used_percentage": 40.0,
      "used_gb": 2.0,
      "total_gb": 5.0
    } | null
  }
}
```

**Notes:**
- `cloud_storage.google_drive` and `cloud_storage.onedrive` are `null` if no account is connected
- `total_bytes` can be `null` for Google Drive if storage is unlimited
- Cloud storage usage is fetched from connected cloud accounts automatically
- Local storage quota is configurable via `DEFAULT_STORAGE_QUOTA_BYTES` environment variable (default: 10 GB)

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Failed to fetch storage usage

**Mock Response:**
```json
{
  "used_bytes": 1024,
  "total_bytes": 10737418240,
  "used_percentage": 0.0,
  "used_gb": 0.0,
  "total_gb": 10.0,
  "cloud_storage": {
    "google_drive": null,
    "onedrive": null
  }
}
```

---

### POST /api/files/upload

Upload a file with chunked encryption and automatic cloud upload.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request:**
- `file`: File to upload (multipart/form-data)
- `parent_id` (optional): Parent folder ID (query parameter)

**Response (201 Created):**
```json
{
  "id": "file-id-123",
  "user_id": "user-id-123",
  "name": "document.pdf",
  "path": "/documents/document.pdf",
  "size": 1024,
  "mime_type": "application/pdf",
  "is_folder": false,
  "parent_id": null,
  "created_at": "2026-01-20T10:00:00Z",
  "updated_at": "2026-01-20T10:00:00Z"
}
```

**Behavior:**
- File is chunked (10MB chunks), encrypted, and stored locally
- If user has a connected cloud account (Google Drive/OneDrive), file chunks are automatically uploaded to cloud in background
- Storage quota is checked before upload (default: 10 GB per user, configurable via `DEFAULT_STORAGE_QUOTA_BYTES`)
- Cloud upload happens asynchronously and doesn't block the API response

**Error Responses:**
- `400 Bad Request`: Invalid file or parent folder not found
- `401 Unauthorized`: Invalid or missing token
- `413 Request Entity Too Large`: Insufficient storage space (quota exceeded)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Upload failed

**Storage Quota:**
- Default quota: 10 GB per user (configurable via `DEFAULT_STORAGE_QUOTA_BYTES` environment variable)
- Quota is checked before upload
- Error message includes available and required space in GB

---

## Data Schemas

### UserResponse
```typescript
{
  id: string (UUID)
  email: string (email format)
  is_active: boolean
  created_at: string (ISO 8601 datetime)
}
```

### FileResponse
```typescript
{
  id: string (UUID)
  user_id: string (UUID)
  name: string
  path: string
  size: number (bytes)
  mime_type: string | null
  is_folder: boolean
  parent_id: string (UUID) | null
  created_at: string (ISO 8601 datetime)
  updated_at: string (ISO 8601 datetime)
}
```

### Token
```typescript
{
  access_token: string
  token_type: "bearer"
}
```

### StorageUsageResponse
```typescript
{
  used_bytes: number
  total_bytes: number
  used_percentage: number
  used_gb: number
  total_gb: number
  cloud_storage: {
    google_drive: CloudStorageUsage | null
    onedrive: CloudStorageUsage | null
  }
}
```

### CloudStorageUsage
```typescript
{
  used_bytes: number
  total_bytes: number | null  // null for unlimited storage
  used_percentage: number
  used_gb: number
  total_gb: number | null  // null for unlimited storage
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Status Codes:**
- `400 Bad Request`: Client error (validation, business logic)
- `401 Unauthorized`: Authentication required or failed
- `404 Not Found`: Resource not found
- `413 Request Entity Too Large`: Storage quota exceeded
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Authentication

All endpoints except `/api/auth/register` and `/api/auth/login` require authentication.

**Header Format:**
```
Authorization: Bearer <access_token>
```

**Token Expiration:** 30 minutes (configurable)

**Token Refresh:** Not implemented in v1.0.0

---

## Change Log

### v1.0.0 (2026-01-22) - Updated with Storage Features
- ✅ POST /api/auth/register
- ✅ POST /api/auth/login
- ✅ GET /api/auth/me
- ✅ GET /api/files
- ✅ POST /api/files/upload (with automatic cloud upload)
- ✅ GET /api/files/storage/usage (local + cloud storage tracking)
- ✅ Storage quota management (10 GB default, configurable)
- ✅ Automatic cloud upload after file upload
- ✅ Cloud storage usage tracking (Google Drive, OneDrive)

---

## Mock Implementation

See `mocks/backend-api/handlers.ts` for MSW mock handlers.

**Quick Start:**
```bash
# In frontend directory
npm install msw
# Use handlers from mocks/backend-api/
```

---

## Integration Notes

- All timestamps are in UTC (ISO 8601 format)
- All IDs are UUIDs (string format)
- File sizes are in bytes
- Empty arrays return `[]`, not `null`

---

**Contract Owner:** Dev 1  
**Contact:** [Slack channel or email]  
**Last Reviewed:** 2026-01-22

---

## Configuration

### Storage Quota

Storage quota per user is configurable via environment variable:

- **Environment Variable**: `DEFAULT_STORAGE_QUOTA_BYTES`
- **Default Value**: `10737418240` (10 GB)
- **Location**: `.env` file or system environment variables
- **Format**: Integer (bytes)

**Examples:**
- 1 GB: `1073741824`
- 5 GB: `5368709120`
- 10 GB: `10737418240` (default)
- 20 GB: `21474836480`
- 50 GB: `53687091200`

### Cloud Storage

Cloud storage usage is automatically fetched from connected cloud accounts:
- **Google Drive**: Requires `drive.metadata.readonly` scope (included in OAuth flow)
- **OneDrive**: Uses Microsoft Graph API `/me/drive/quota` endpoint
- Cloud storage usage is included in `/api/files/storage/usage` response
- If no cloud account is connected, `cloud_storage` fields are `null`
