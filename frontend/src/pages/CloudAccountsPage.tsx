// Cloud Accounts Page based on Cloud Accounts API Contract v1.0.0

import { useEffect, useState } from 'react'
import { useCloudAccountsStore } from '@/store/cloudAccountsStore'
import { cloudAccountService } from '@/services/cloudAccountService'
import { CloudProvider } from '@/types/api'
import './CloudAccountsPage.css'

export default function CloudAccountsPage() {
  const { accounts, isLoading, error, fetchAccounts, disconnectAccount, clearError } =
    useCloudAccountsStore()
  const [connectingProvider, setConnectingProvider] = useState<CloudProvider | null>(null)
  const [oauthState, setOauthState] = useState<string | null>(null)

  useEffect(() => {
    fetchAccounts()
    
    // Check for OAuth callback
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const state = urlParams.get('state')
    const provider = urlParams.get('provider') as CloudProvider | null

    if (code && state && provider) {
      handleOAuthCallback(provider, code, state)
    }
  }, [])

  const handleOAuthCallback = async (provider: CloudProvider, code: string, state: string) => {
    try {
      // Verify state matches stored state
      const storedState = sessionStorage.getItem('oauth_state')
      if (storedState !== state) {
        throw new Error('Invalid state parameter')
      }

      await cloudAccountService.handleCallback(provider, code, state)
      
      // Clean up
      sessionStorage.removeItem('oauth_state')
      setOauthState(null)
      
      // Refresh accounts list
      await fetchAccounts()
      
      // Clean URL
      window.history.replaceState({}, '', '/cloud-accounts')
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to connect account'
      clearError()
      alert(errorMessage)
    }
  }

  const handleConnect = async (provider: CloudProvider) => {
    try {
      setConnectingProvider(provider)
      clearError()

      // Generate redirect URI
      const redirectUri = `${window.location.origin}/cloud-accounts?provider=${provider}`
      
      const { oauth_url, state } = await cloudAccountService.initiateOAuth(provider, redirectUri)
      
      // Store state for verification
      sessionStorage.setItem('oauth_state', state)
      setOauthState(state)

      // Open OAuth URL in same window (or popup)
      window.location.href = oauth_url
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to initiate OAuth'
      setConnectingProvider(null)
      alert(errorMessage)
    }
  }

  const handleDisconnect = async (accountId: string) => {
    if (!confirm('Are you sure you want to disconnect this account?')) {
      return
    }

    try {
      await disconnectAccount(accountId)
    } catch (error) {
      // Error handled by store
    }
  }

  const getProviderName = (provider: CloudProvider): string => {
    switch (provider) {
      case 'google_drive':
        return 'Google Drive'
      case 'onedrive':
        return 'OneDrive'
      default:
        return provider
    }
  }

  const getProviderIcon = (provider: CloudProvider): string => {
    switch (provider) {
      case 'google_drive':
        return '📁'
      case 'onedrive':
        return '☁️'
      default:
        return '📦'
    }
  }

  const isAccountConnected = (provider: CloudProvider): boolean => {
    return accounts.some((acc) => acc.provider === provider && acc.is_connected)
  }

  const getAccountForProvider = (provider: CloudProvider) => {
    return accounts.find((acc) => acc.provider === provider)
  }

  const providers: CloudProvider[] = ['google_drive', 'onedrive']

  return (
    <div className="cloud-accounts-page">
      <div className="container">
        <div className="cloud-accounts-header">
          <div>
            <h1 className="page-title">Cloud Accounts</h1>
            <p className="page-subtitle">
              Connect your cloud storage accounts to automatically sync your files
            </p>
          </div>
        </div>

        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button onClick={clearError} className="btn-close">×</button>
          </div>
        )}

        <div className="cloud-accounts-grid">
          {providers.map((provider) => {
            const account = getAccountForProvider(provider)
            const isConnected = isAccountConnected(provider)
            const isConnecting = connectingProvider === provider

            return (
              <div key={provider} className="cloud-account-card">
                <div className="account-icon">{getProviderIcon(provider)}</div>
                <h3 className="account-name">{getProviderName(provider)}</h3>
                
                {isConnected && account ? (
                  <div className="account-status connected">
                    <span className="status-indicator"></span>
                    <span>Connected</span>
                  </div>
                ) : (
                  <div className="account-status disconnected">
                    <span className="status-indicator"></span>
                    <span>Not Connected</span>
                  </div>
                )}

                {account && (
                  <div className="account-details">
                    <p className="account-email">{account.provider_account_id}</p>
                    {account.token_expires_at && (
                      <p className="account-expiry">
                        Expires: {new Date(account.token_expires_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                )}

                <div className="account-actions">
                  {isConnected && account ? (
                    <button
                      onClick={() => handleDisconnect(account.id)}
                      className="btn btn-danger btn-full"
                      disabled={isLoading}
                    >
                      Disconnect
                    </button>
                  ) : (
                    <button
                      onClick={() => handleConnect(provider)}
                      className="btn btn-primary btn-full"
                      disabled={isConnecting || isLoading}
                    >
                      {isConnecting ? (
                        <>
                          <span className="loading"></span>
                          Connecting...
                        </>
                      ) : (
                        'Connect'
                      )}
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {accounts.length > 0 && (
          <div className="connected-accounts-list">
            <h2 className="section-title">Connected Accounts</h2>
            <div className="accounts-table">
              {accounts.map((account) => (
                <div key={account.id} className="account-row">
                  <div className="account-info">
                    <span className="account-icon-small">{getProviderIcon(account.provider)}</span>
                    <div>
                      <p className="account-name-small">{getProviderName(account.provider)}</p>
                      <p className="account-email-small">{account.provider_account_id}</p>
                    </div>
                  </div>
                  <div className="account-status-cell">
                    {account.is_connected ? (
                      <span className="badge badge-success">Connected</span>
                    ) : (
                      <span className="badge badge-error">Disconnected</span>
                    )}
                  </div>
                  <button
                    onClick={() => handleDisconnect(account.id)}
                    className="btn btn-outline btn-sm"
                  >
                    Disconnect
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
