// Cloud Account Service based on Cloud Accounts API Contract v1.0.0

import apiClient from './apiClient'
import {
  CloudAccount,
  CloudAccountListResponse,
  CloudProvider,
  OAuthInitiateResponse,
  OAuthCallbackResponse,
} from '@/types/api'

export const cloudAccountService = {
  async listAccounts(): Promise<CloudAccountListResponse> {
    const response = await apiClient.get<CloudAccountListResponse>('/cloud-accounts')
    return response.data
  },

  async initiateOAuth(provider: CloudProvider, redirectUri: string): Promise<OAuthInitiateResponse> {
    const response = await apiClient.post<OAuthInitiateResponse>(
      `/cloud-accounts/connect/${provider}`,
      {},
      {
        params: { redirect_uri: redirectUri },
      }
    )
    return response.data
  },

  async handleCallback(
    provider: CloudProvider,
    code: string,
    state: string
  ): Promise<OAuthCallbackResponse> {
    const response = await apiClient.get<OAuthCallbackResponse>(
      `/cloud-accounts/callback/${provider}`,
      {
        params: { code, state },
      }
    )
    return response.data
  },

  async disconnectAccount(accountId: string): Promise<void> {
    await apiClient.delete(`/cloud-accounts/${accountId}`)
  },

  async refreshToken(accountId: string): Promise<void> {
    await apiClient.post(`/cloud-accounts/${accountId}/refresh`)
  },

  async getAccountStatus(accountId: string): Promise<CloudAccount> {
    const response = await apiClient.get<CloudAccount>(`/cloud-accounts/${accountId}/status`)
    return response.data
  },
}
