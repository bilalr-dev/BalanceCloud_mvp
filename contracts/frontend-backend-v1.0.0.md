# Frontend-Backend Integration Contract v1.0.0

**Owner:** Dev 2 (Frontend)  
**Version:** 1.0.0  
**Status:** 📝 Draft  
**Last Updated:** 2026-01-20  
**Dependencies:** 
- Backend API Contract v1.0.0

---

## Overview

This contract defines how the Frontend integrates with the Backend API. It specifies the frontend's expectations, error handling patterns, and integration points.

---

## Integration Points

### Authentication Flow

**Registration Flow:**
1. User submits registration form
2. Frontend calls `POST /api/auth/register`
3. On success: Store token, redirect to dashboard
4. On error: Display error message from `detail` field

**Login Flow:**
1. User submits login form
2. Frontend calls `POST /api/auth/login`
3. On success: Store token in localStorage, redirect to dashboard
4. On error: Display "Incorrect email or password"

**Token Storage:**
- Store `access_token` in `localStorage` (key: `auth_token`)
- Include in all API requests: `Authorization: Bearer ${token}`
- Token expires after 30 minutes (handle expiration)

---

### File Management Flow

**List Files:**
1. On page load, call `GET /api/files?parent_id=<folder_id>`
2. Display files in UI
3. Handle empty list (show "No files" message)

**Error Handling:**
- `401`: Redirect to login page
- `500`: Show "Server error, please try again"

---

## Frontend Expectations

### API Client Configuration

```typescript
const API_BASE_URL = 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

---

## Mock Usage During Development

**Phase 1: Mock Development (Backend not ready)**
- Use MSW mock handlers from `mocks/backend-api/handlers.ts`
- Develop UI components independently
- Test all error cases using mocks

**Phase 2: Integration (Backend Stable)**
- Switch from mock to real API
- Update `API_BASE_URL` if needed
- Run end-to-end tests

---

## Error Handling Patterns

### Network Errors
```typescript
try {
  const response = await apiClient.post('/auth/login', credentials)
  // Handle success
} catch (error) {
  if (error.response) {
    // Server responded with error
    const message = error.response.data.detail || 'An error occurred'
    showError(message)
  } else {
    // Network error
    showError('Network error. Please check your connection.')
  }
}
```

### Validation Errors
- Display field-level errors for `422` responses
- Show general error message for other status codes

---

## Cloud Accounts Flow

**Based on:** TASKS_PLANING.md - Day 1-4 tasks for Frontend

### Connect Cloud Account Flow:
1. User clicks "Connect Google Drive" or "Connect OneDrive"
2. Frontend calls `POST /api/cloud-accounts/connect/{provider}?redirect_uri=...`
3. Backend returns `oauth_url` and `state`
4. Frontend stores `state` in sessionStorage
5. Frontend opens OAuth URL in popup or redirects
6. User authorizes on provider site
7. Provider redirects to `redirect_uri` with `code` and `state`
8. Frontend calls `GET /api/cloud-accounts/callback/{provider}?code=...&state=...`
9. Backend exchanges code for tokens and stores account
10. Frontend updates UI to show connected account

### List Cloud Accounts:
1. On CloudAccountsPage load, call `GET /api/cloud-accounts`
2. Display account cards for each provider
3. Show connection status (connected/disconnected)
4. Show token expiration status

### Disconnect Cloud Account:
1. User clicks "Disconnect" on account card
2. Frontend calls `DELETE /api/cloud-accounts/{account_id}`
3. On success: Remove account from UI
4. On error: Show error message

---

## File Management with Cloud Storage

### Upload Flow (with Cloud):
1. User selects file to upload
2. Frontend calls `POST /api/files/upload` (same as before)
3. Backend encrypts and chunks file
4. Backend uploads chunks to cloud storage (if cloud account connected)
5. Frontend shows upload progress
6. On completion: Show success message

### Download Flow (from Cloud):
1. User clicks download on file
2. Frontend calls `GET /api/files/{file_id}/download`
3. Backend fetches chunks from cloud storage
4. Backend decrypts and reassembles file
5. Frontend receives file stream
6. Frontend triggers browser download

### Cloud Storage Indicators:
- Show cloud icon next to files stored in cloud
- Show provider badge (Google Drive, OneDrive)
- Show sync status (synced, syncing, error)

---

## Change Log

### v1.0.0 (2026-01-20) - Initial Draft
- Authentication flow defined
- File management flow defined
- Error handling patterns defined
- Cloud accounts flow defined
- Cloud storage integration defined

---

## Implementation Tasks (from TASKS_PLANING.md)

### Day 1: Frontend Planning & Setup
- [ ] Review full version frontend structure
- [ ] Plan cloud accounts UI components
- [ ] Set up cloud account store (Zustand)
- [ ] Create cloud account service skeleton
- [ ] Design OAuth callback flow
- [ ] Update routing for cloud accounts page

### Day 2: Cloud Accounts Frontend
- [ ] Build cloud accounts page UI
- [ ] Implement OAuth popup flow
- [ ] Create cloud account cards (Google Drive, OneDrive)
- [ ] Add connect/disconnect functionality
- [ ] Handle OAuth callbacks
- [ ] Display connection status

### Day 3: File Management UI Enhancements
- [ ] Update FilesPage with cloud storage indicators
- [ ] Add file upload progress
- [ ] Improve file list UI
- [ ] Add cloud storage status
- [ ] Enhance breadcrumb navigation
- [ ] Add file preview (if time permits)

### Day 4: Frontend Integration & Polish
- [ ] Integrate cloud upload/download in UI
- [ ] Add loading states
- [ ] Improve error messages
- [ ] Add success notifications
- [ ] Polish UI/UX
- [ ] Test complete user flow

---

**Contract Owner:** Mouhamad (Frontend)  
**Status:** Draft - Implementation in progress per TASKS_PLANING.md
