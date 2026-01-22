// API Types based on Backend API Contract v1.0.0

export interface Token {
  access_token: string
  token_type: 'bearer'
}

export interface User {
  id: string
  email: string
  is_active: boolean
  created_at: string
}

export interface File {
  id: string
  user_id: string
  name: string
  path: string
  size: number
  mime_type: string | null
  is_folder: boolean
  parent_id: string | null
  created_at: string
  updated_at: string
}

export interface FileListResponse {
  files: File[]
  total: number
}

export interface CloudStorageUsage {
  used_bytes: number
  total_bytes: number | null
  used_percentage: number
  used_gb: number
  total_gb: number | null
}

export interface StorageUsageResponse {
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

// Cloud Accounts API Types
export type CloudProvider = 'google_drive' | 'onedrive'

export interface CloudAccount {
  id: string
  provider: CloudProvider
  provider_account_id: string
  is_connected: boolean
  token_expires_at: string | null
  created_at: string
  updated_at: string
}

export interface CloudAccountListResponse {
  accounts: CloudAccount[]
  total: number
}

export interface OAuthInitiateResponse {
  oauth_url: string
  state: string
}

export interface OAuthCallbackResponse {
  account_id: string
  provider: CloudProvider
  provider_account_id: string
  is_connected: boolean
  message: string
}

export interface ErrorResponse {
  detail: string
}
