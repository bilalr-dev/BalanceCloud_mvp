# Backend API Contract v1.0.0

**Owner:** Dev 1 (Backend Infrastructure)  
**Version:** 1.0.0  
**Status:** ✅ Stable  
**Last Updated:** 2026-01-20  
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

### v1.0.0 (2026-01-20) - Initial Stable Release
- ✅ POST /api/auth/register
- ✅ POST /api/auth/login
- ✅ GET /api/auth/me
- ✅ GET /api/files

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
**Last Reviewed:** 2026-01-20
