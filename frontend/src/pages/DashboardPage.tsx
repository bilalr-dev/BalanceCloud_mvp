// Dashboard Page - Shows storage information only

import { useEffect } from 'react'
import { useFilesStore } from '@/store/filesStore'
import { useAuthStore } from '@/store/authStore'

export default function DashboardPage() {
  const { storageUsage, fetchStorageUsage, isFetchingStorageUsage } = useFilesStore()
  const { isAuthenticated, isLoading: isAuthLoading } = useAuthStore()

  useEffect(() => {
    // Only fetch storage usage if user is authenticated and has a valid token
    const token = localStorage.getItem('auth_token')
    if (isAuthenticated && !isAuthLoading && token) {
      fetchStorageUsage()
    }
  }, [fetchStorageUsage, isAuthenticated, isAuthLoading])

  // Helper function to format bytes
  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  // Storage Card Component
  const StorageCard = ({ 
    title, 
    icon, 
    usedBytes, 
    totalBytes, 
    percentage, 
    isConnected, 
    color = 'blue',
    isLoading = false 
  }: {
    title: string
    icon: string
    usedBytes: number | null
    totalBytes: number | null
    percentage: number | null
    isConnected: boolean
    color?: 'blue' | 'green' | 'purple'
    isLoading?: boolean
  }) => {
    const colorClasses = {
      blue: {
        bg: 'bg-blue-50 dark:bg-blue-900/10',
        iconBg: 'bg-blue-100 dark:bg-blue-900/30',
        progress: 'bg-blue-500',
        text: 'text-blue-600 dark:text-blue-400'
      },
      green: {
        bg: 'bg-green-50 dark:bg-green-900/10',
        iconBg: 'bg-green-100 dark:bg-green-900/30',
        progress: 'bg-green-500',
        text: 'text-green-600 dark:text-green-400'
      },
      purple: {
        bg: 'bg-purple-50 dark:bg-purple-900/10',
        iconBg: 'bg-purple-100 dark:bg-purple-900/30',
        progress: 'bg-purple-500',
        text: 'text-purple-600 dark:text-purple-400'
      }
    }

    const colors = colorClasses[color]
    const progressColor = percentage && percentage > 90 
      ? 'bg-red-500' 
      : percentage && percentage > 70 
      ? 'bg-yellow-500' 
      : colors.progress

    if (isLoading) {
      return (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 shadow-sm">
          <div className="flex items-center justify-center h-64">
            <div className="flex flex-col items-center gap-3">
              <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-sm text-gray-600 dark:text-gray-400">Loading...</span>
            </div>
          </div>
        </div>
      )
    }

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 shadow-sm hover:shadow-md transition-shadow">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-xl ${colors.iconBg} flex items-center justify-center`}>
              <span className="text-3xl">{icon}</span>
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">{title}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {isConnected ? 'Connected' : 'Not connected'}
              </p>
            </div>
          </div>
          <span className={`px-3 py-1.5 text-xs font-semibold rounded-full ${
            isConnected
              ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
          }`}>
            {isConnected ? 'Active' : 'Inactive'}
          </span>
        </div>

        {isConnected && usedBytes !== null && totalBytes !== null && percentage !== null ? (
          <>
            {/* Storage Stats */}
            <div className="mb-6">
              <div className="flex items-baseline justify-between mb-4">
                <div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    {formatBytes(usedBytes)}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    of {formatBytes(totalBytes)} used
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    {percentage.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">used</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="relative">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                  <div
                    className={`h-3 rounded-full ${progressColor} transition-all duration-500 ease-out`}
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  ></div>
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
                  <span>0 GB</span>
                  <span>{formatBytes(totalBytes)}</span>
                </div>
              </div>
            </div>

            {/* Additional Info */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Available</span>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">
                  {formatBytes(totalBytes - usedBytes)}
                </span>
              </div>
            </div>
          </>
        ) : (
          <div className="py-8 text-center">
            <div className="text-gray-400 dark:text-gray-500 mb-2">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">No storage data available</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Connect your account to view usage</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Storage Dashboard</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Monitor your storage usage across all connected services
          </p>
        </div>
        <button
          onClick={() => fetchStorageUsage()}
          disabled={isFetchingStorageUsage}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Storage Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Local Storage */}
        <StorageCard
          title="Local Storage"
          icon="💾"
          usedBytes={storageUsage?.used_bytes || null}
          totalBytes={storageUsage?.total_bytes || null}
          percentage={storageUsage?.used_percentage || null}
          isConnected={!!storageUsage}
          color="blue"
          isLoading={isFetchingStorageUsage || !storageUsage}
        />

        {/* Google Drive */}
        <StorageCard
          title="Google Drive"
          icon="📁"
          usedBytes={storageUsage?.cloud_storage?.google_drive?.used_bytes || null}
          totalBytes={storageUsage?.cloud_storage?.google_drive?.total_bytes || null}
          percentage={storageUsage?.cloud_storage?.google_drive?.used_percentage || null}
          isConnected={!!storageUsage?.cloud_storage?.google_drive}
          color="green"
          isLoading={isFetchingStorageUsage || !storageUsage}
        />

        {/* OneDrive */}
        <StorageCard
          title="OneDrive"
          icon="☁️"
          usedBytes={storageUsage?.cloud_storage?.onedrive?.used_bytes || null}
          totalBytes={storageUsage?.cloud_storage?.onedrive?.total_bytes || null}
          percentage={storageUsage?.cloud_storage?.onedrive?.used_percentage || null}
          isConnected={!!storageUsage?.cloud_storage?.onedrive}
          color="purple"
          isLoading={isFetchingStorageUsage || !storageUsage}
        />

        {/* Dropbox - UI Only, No Functionality */}
        <StorageCard
          title="Dropbox"
          icon="📦"
          usedBytes={null}
          totalBytes={null}
          percentage={null}
          isConnected={false}
          color="blue"
          isLoading={false}
        />
      </div>

      {/* Summary Stats */}
      {storageUsage && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Storage</div>
              <div className="text-xl font-bold text-gray-900 dark:text-white">
                {formatBytes(storageUsage.total_bytes)}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Used Storage</div>
              <div className="text-xl font-bold text-gray-900 dark:text-white">
                {formatBytes(storageUsage.used_bytes)}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Available Storage</div>
              <div className="text-xl font-bold text-gray-900 dark:text-white">
                {formatBytes(storageUsage.total_bytes - storageUsage.used_bytes)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
