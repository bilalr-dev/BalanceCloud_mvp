export interface User {
  id: string
  email: string
  created_at: string
}

export interface File {
  id: string
  name: string
  size: number
  mime_type: string
  is_folder: boolean
  parent_id: string | null
  created_at: string
  updated_at: string
}

export interface CloudAccount {
  id: string
  provider: 'google_drive' | 'onedrive'
  provider_account_id: string
  is_connected: boolean
  token_expires_at: string | null
  created_at: string
  updated_at: string
}
