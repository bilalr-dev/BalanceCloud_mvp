import apiClient from './apiClient'

export interface CloudAccount {
  id: string
  provider: 'google_drive' | 'onedrive'
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
  provider: 'google_drive' | 'onedrive'
  provider_account_id: string
  is_connected: boolean
  message: string
}

export const cloudAccountService = {
  listAccounts: async (): Promise<CloudAccountListResponse> => {
    const response = await apiClient.get<CloudAccountListResponse>('/cloud-accounts')
    return response.data
  },

  initiateOAuth: async (
    provider: 'google_drive' | 'onedrive',
    redirectUri: string
  ): Promise<OAuthInitiateResponse> => {
    const response = await apiClient.post<OAuthInitiateResponse>(
      `/cloud-accounts/connect/${provider}`,
      null,
      {
        params: { redirect_uri: redirectUri },
      }
    )
    return response.data
  },

  handleCallback: async (
    provider: 'google_drive' | 'onedrive',
    code: string,
    state: string
  ): Promise<OAuthCallbackResponse> => {
    const response = await apiClient.get<OAuthCallbackResponse>(
      `/cloud-accounts/callback/${provider}`,
      {
        params: { code, state },
      }
    )
    return response.data
  },

  disconnectAccount: async (accountId: string): Promise<void> => {
    await apiClient.delete(`/cloud-accounts/${accountId}`)
  },

  refreshToken: async (accountId: string): Promise<void> => {
    await apiClient.post(`/cloud-accounts/${accountId}/refresh`)
  },
}
