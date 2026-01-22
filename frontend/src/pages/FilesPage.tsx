// Files Page based on Frontend-Backend Contract v1.0.0

import { useEffect, useRef } from 'react'
import { useFilesStore } from '@/store/filesStore'
import { useCloudAccountsStore } from '@/store/cloudAccountsStore'
import { File as FileType } from '@/types/api'
import './FilesPage.css'

export default function FilesPage() {
  const {
    files,
    currentFolderId,
    storageUsage,
    isLoading,
    isUploading,
    uploadProgress,
    error,
    fetchFiles,
    uploadFile,
    downloadFile,
    fetchStorageUsage,
    setCurrentFolder,
    clearError,
  } = useFilesStore()

  const { accounts } = useCloudAccountsStore()
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchFiles(currentFolderId || undefined)
    fetchStorageUsage()
  }, [currentFolderId])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleUpload(file)
    }
  }

  const handleUpload = async (file: File) => {
    try {
      await uploadFile(file, currentFolderId || undefined)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      // Error handled by store
    }
  }

  const handleDownload = async (file: FileType) => {
    try {
      await downloadFile(file.id, file.name)
    } catch (err) {
      // Error handled by store
    }
  }

  const handleFolderClick = (folder: FileType) => {
    setCurrentFolder(folder.id)
  }

  const handleBack = () => {
    setCurrentFolder(null)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getCloudProvider = (file: FileType): string | null => {
    // Check if file is stored in cloud (this would come from backend in real implementation)
    // For now, we'll show cloud icon if user has connected accounts
    return accounts.length > 0 ? 'cloud' : null
  }

  return (
    <div className="files-page">
      <div className="container">
        <div className="files-header">
          <div>
            <h1 className="page-title">My Files</h1>
            {storageUsage && (
              <p className="storage-info">
                Storage: {storageUsage.used_gb.toFixed(2)} GB / {storageUsage.total_gb.toFixed(2)} GB
                ({storageUsage.used_percentage.toFixed(1)}%)
              </p>
            )}
          </div>
          <div className="files-actions">
            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn btn-primary"
              disabled={isUploading}
            >
              {isUploading ? (
                <>
                  <span className="loading"></span>
                  Uploading... {uploadProgress}%
                </>
              ) : (
                'Upload File'
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button onClick={clearError} className="btn-close">×</button>
          </div>
        )}

        {currentFolderId && (
          <div className="breadcrumb">
            <button onClick={handleBack} className="btn btn-outline btn-sm">
              ← Back
            </button>
          </div>
        )}

        <div className="files-content">
          {isLoading ? (
            <div className="loading-state">
              <span className="loading"></span>
              <span>Loading files...</span>
            </div>
          ) : files.length === 0 ? (
            <div className="empty-state">
              <p>No files yet</p>
              <p className="empty-state-subtitle">Upload your first file to get started</p>
            </div>
          ) : (
            <div className="files-grid">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="file-card"
                  onClick={() => file.is_folder && handleFolderClick(file)}
                >
                  <div className="file-icon">
                    {file.is_folder ? (
                      <span className="icon-folder">📁</span>
                    ) : (
                      <span className="icon-file">📄</span>
                    )}
                    {getCloudProvider(file) && (
                      <span className="cloud-badge" title="Stored in cloud">☁️</span>
                    )}
                  </div>
                  <div className="file-info">
                    <h3 className="file-name" title={file.name}>
                      {file.name}
                    </h3>
                    <p className="file-meta">
                      {file.is_folder
                        ? 'Folder'
                        : `${formatFileSize(file.size)} • ${new Date(file.created_at).toLocaleDateString()}`}
                    </p>
                  </div>
                  {!file.is_folder && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDownload(file)
                      }}
                      className="btn-download"
                      title="Download"
                    >
                      ⬇️
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
