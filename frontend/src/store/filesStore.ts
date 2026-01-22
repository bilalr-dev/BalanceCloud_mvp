// Files Store using Zustand

import { create } from 'zustand'
import { File as FileType, StorageUsageResponse } from '@/types/api'
import { fileService } from '@/services/fileService'

interface FilesState {
  files: FileType[]
  currentFolderId: string | null
  storageUsage: StorageUsageResponse | null
  isLoading: boolean
  isUploading: boolean
  uploadProgress: number
  error: string | null
  fetchFiles: (parentId?: string) => Promise<void>
  uploadFile: (file: File, parentId?: string) => Promise<void>
  downloadFile: (fileId: string, fileName: string) => Promise<void>
  fetchStorageUsage: () => Promise<void>
  setCurrentFolder: (folderId: string | null) => void
  clearError: () => void
}

export const useFilesStore = create<FilesState>((set, get) => ({
  files: [],
  currentFolderId: null,
  storageUsage: null,
  isLoading: false,
  isUploading: false,
  uploadProgress: 0,
  error: null,

  fetchFiles: async (parentId?: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await fileService.listFiles(parentId)
      set({
        files: response.files,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch files'
      set({
        isLoading: false,
        error: errorMessage,
      })
    }
  },

  uploadFile: async (file: File, parentId?: string) => {
    set({ isUploading: true, uploadProgress: 0, error: null })
    try {
      // Simulate progress (actual progress would come from axios upload progress)
      const progressInterval = setInterval(() => {
        set((state) => ({
          uploadProgress: Math.min(state.uploadProgress + 10, 90),
        }))
      }, 200)

      const uploadedFile = await fileService.uploadFile(file, parentId)
      
      clearInterval(progressInterval)
      set({ uploadProgress: 100 })

      // Refresh file list
      await get().fetchFiles(parentId)

      set({
        isUploading: false,
        uploadProgress: 0,
        error: null,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Upload failed'
      set({
        isUploading: false,
        uploadProgress: 0,
        error: errorMessage,
      })
      throw error
    }
  },

  downloadFile: async (fileId: string, fileName: string) => {
    try {
      const blob = await fileService.downloadFile(fileId)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Download failed'
      set({ error: errorMessage })
      throw error
    }
  },

  fetchStorageUsage: async () => {
    try {
      const usage = await fileService.getStorageUsage()
      set({ storageUsage: usage })
    } catch (error: any) {
      console.error('Failed to fetch storage usage:', error)
    }
  },

  setCurrentFolder: (folderId: string | null) => {
    set({ currentFolderId: folderId })
  },

  clearError: () => {
    set({ error: null })
  },
}))
