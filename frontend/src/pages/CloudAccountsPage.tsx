import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useCloudAccountsStore } from '../store/cloudAccountsStore'
import { cloudAccountService } from '../services/cloudAccountService'

export default function CloudAccountsPage() {
  const navigate = useNavigate()
  const { token } = useAuthStore()
  const { accounts, setAccounts, loading, setLoading, error, setError, removeAccount } =
    useCloudAccountsStore()

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    loadAccounts()
  }, [token, navigate])

  const loadAccounts = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await cloudAccountService.listAccounts()
      setAccounts(response.accounts)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load cloud accounts')
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async (provider: 'google_drive' | 'onedrive') => {
    try {
      const redirectUri = `${window.location.origin}/oauth/callback`
      const response = await cloudAccountService.initiateOAuth(provider, redirectUri)
      
      // Store state for verification
      sessionStorage.setItem(`oauth_state_${provider}`, response.state)
      sessionStorage.setItem(`oauth_redirect_uri_${provider}`, redirectUri)
      
      // Redirect to OAuth URL
      window.location.href = response.oauth_url
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initiate OAuth flow')
    }
  }

  const handleDisconnect = async (accountId: string) => {
    if (!confirm('Are you sure you want to disconnect this account?')) return

    try {
      await cloudAccountService.disconnectAccount(accountId)
      removeAccount(accountId)
      loadAccounts()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disconnect account')
    }
  }

  const getProviderIcon = (provider: string) => {
    return provider === 'google_drive' ? '📁' : '☁️'
  }

  const getProviderName = (provider: string) => {
    return provider === 'google_drive' ? 'Google Drive' : 'OneDrive'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-blue-600 hover:text-blue-500"
              >
                ← Dashboard
              </button>
              <h1 className="text-xl font-bold text-gray-900">Cloud Accounts</h1>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900">Connect Cloud Storage</h2>
            <p className="mt-2 text-gray-600">
              Connect your cloud storage accounts to upload and sync files
            </p>
          </div>

          {error && (
            <div className="p-4 bg-red-50 border-l-4 border-red-400">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <button
                onClick={() => handleConnect('google_drive')}
                className="p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
              >
                <div className="flex items-center mb-2">
                  <span className="text-3xl mr-3">📁</span>
                  <h3 className="text-lg font-semibold text-gray-900">Google Drive</h3>
                </div>
                <p className="text-gray-600">Connect your Google Drive account</p>
              </button>

              <button
                onClick={() => handleConnect('onedrive')}
                className="p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
              >
                <div className="flex items-center mb-2">
                  <span className="text-3xl mr-3">☁️</span>
                  <h3 className="text-lg font-semibold text-gray-900">OneDrive</h3>
                </div>
                <p className="text-gray-600">Connect your OneDrive account</p>
              </button>
            </div>

            {loading ? (
              <div className="text-center text-gray-500 py-8">Loading accounts...</div>
            ) : accounts.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                No cloud accounts connected yet.
              </div>
            ) : (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Connected Accounts</h3>
                {accounts.map((account) => (
                  <div
                    key={account.id}
                    className="p-4 border border-gray-200 rounded-lg flex justify-between items-center"
                  >
                    <div>
                      <div className="flex items-center">
                        <span className="text-2xl mr-3">{getProviderIcon(account.provider)}</span>
                        <div>
                          <p className="font-semibold text-gray-900">
                            {getProviderName(account.provider)}
                          </p>
                          <p className="text-sm text-gray-500">{account.provider_account_id}</p>
                          <p className="text-xs text-gray-400">
                            {account.is_connected ? '✅ Connected' : '❌ Disconnected'}
                          </p>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDisconnect(account.id)}
                      className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                      Disconnect
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
