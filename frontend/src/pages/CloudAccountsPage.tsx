// Cloud Accounts Page - Storage Health Design

import { useEffect, useState } from 'react'
import { useCloudAccountsStore } from '@/store/cloudAccountsStore'
import { cloudAccountService } from '@/services/cloudAccountService'
import { CloudProvider } from '@/types/api'
import { useFilesStore } from '@/store/filesStore'

export default function CloudAccountsPage() {
  const { accounts, isLoading, error, fetchAccounts, disconnectAccount, clearError } =
    useCloudAccountsStore()
  const { storageUsage, fetchStorageUsage } = useFilesStore()
  const [connectingProvider, setConnectingProvider] = useState<CloudProvider | null>(null)

  useEffect(() => {
    fetchAccounts()
    // Always fetch storage usage to ensure it's up to date
    fetchStorageUsage()
    
    // Check for OAuth callback
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const state = urlParams.get('state')
    const provider = urlParams.get('provider') as CloudProvider | null

    if (code && state && provider) {
      handleOAuthCallback(provider, code, state)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Only run once on mount

  const handleOAuthCallback = async (provider: CloudProvider, code: string, state: string) => {
    try {
      const storedState = sessionStorage.getItem('oauth_state')
      if (storedState !== state) {
        throw new Error('Invalid state parameter')
      }

      await cloudAccountService.handleCallback(provider, code, state)
      sessionStorage.removeItem('oauth_state')
      await fetchAccounts()
      await fetchStorageUsage()
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

      const redirectUri = `${window.location.origin}/cloud-accounts?provider=${provider}`
      const { oauth_url, state } = await cloudAccountService.initiateOAuth(provider, redirectUri)
      
      sessionStorage.setItem('oauth_state', state)
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
      await fetchStorageUsage()
    } catch (error) {
      // Error handled by store
    }
  }

  const getProviderInfo = (provider: CloudProvider) => {
    switch (provider) {
      case 'google_drive':
        return { name: 'Google Drive', icon: '📁', color: 'blue' }
      case 'onedrive':
        return { name: 'OneDrive', icon: '☁️', color: 'blue' }
      default:
        return { name: provider, icon: '📦', color: 'gray' }
    }
  }

  const getAccountForProvider = (provider: CloudProvider) => {
    return accounts.find((acc) => acc.provider === provider && acc.is_connected)
  }

  const getCloudStorageUsage = (provider: CloudProvider) => {
    if (!storageUsage) return null
    return storageUsage.cloud_storage[provider]
  }

  const providers: CloudProvider[] = ['google_drive', 'onedrive']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Storage Health</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Monitor your cloud storage accounts and usage
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              fetchStorageUsage()
              fetchAccounts()
            }}
            className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          <button className="text-sm text-blue-600 dark:text-blue-400 hover:underline font-medium">
            Manage Quotas
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center justify-between">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button onClick={clearError} className="text-red-600 dark:text-red-400 hover:text-red-700">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Storage Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {providers.map((provider) => {
          const account = getAccountForProvider(provider)
          const isConnected = !!account
          const info = getProviderInfo(provider)
          const cloudUsage = getCloudStorageUsage(provider)
          const isConnecting = connectingProvider === provider

          return (
            <div
              key={provider}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{info.icon}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">{info.name}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {isConnected ? account.provider_account_id : 'Not connected'}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded ${
                  isConnected
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                }`}>
                  {isConnected ? 'Healthy' : 'Disconnected'}
                </span>
              </div>

              {isConnected && cloudUsage && (
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600 dark:text-gray-400">
                      {cloudUsage.used_gb.toFixed(1)} GB / {cloudUsage.total_gb?.toFixed(1) || '∞'} GB
                    </span>
                    <span className="text-gray-600 dark:text-gray-400">
                      {cloudUsage.used_percentage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        cloudUsage.used_percentage > 90
                          ? 'bg-red-500'
                          : cloudUsage.used_percentage > 70
                          ? 'bg-yellow-500'
                          : 'bg-blue-500'
                      }`}
                      style={{ width: `${Math.min(cloudUsage.used_percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {!isConnected && (
                <div className="mb-4">
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">No storage data available</p>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-gray-300 dark:bg-gray-600" style={{ width: '0%' }}></div>
                  </div>
                </div>
              )}

              <div className="mt-4">
                {isConnected ? (
                  <button
                    onClick={() => handleDisconnect(account.id)}
                    className="w-full px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors disabled:opacity-50"
                    disabled={isLoading}
                  >
                    Disconnect
                  </button>
                ) : (
                  <button
                    onClick={() => handleConnect(provider)}
                    className="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    disabled={isConnecting || isLoading}
                  >
                    {isConnecting ? (
                      <>
                        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
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

      {/* Local Storage Card */}
      {storageUsage && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="text-3xl">💾</span>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Local Storage</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Primary storage</p>
              </div>
            </div>
            <span className="px-2 py-1 text-xs font-medium rounded bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
              Healthy
            </span>
          </div>

          <div className="mb-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-gray-600 dark:text-gray-400">
                {storageUsage.used_gb < 0.01 
                  ? `${(storageUsage.used_bytes / (1024 * 1024)).toFixed(2)} MB / ${storageUsage.total_gb.toFixed(2)} GB`
                  : `${storageUsage.used_gb.toFixed(2)} GB / ${storageUsage.total_gb.toFixed(2)} GB`}
              </span>
              <span className="text-gray-600 dark:text-gray-400">
                {storageUsage.used_percentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  storageUsage.used_percentage > 90
                    ? 'bg-red-500'
                    : storageUsage.used_percentage > 70
                    ? 'bg-yellow-500'
                    : 'bg-blue-500'
                }`}
                style={{ width: `${Math.min(storageUsage.used_percentage, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
