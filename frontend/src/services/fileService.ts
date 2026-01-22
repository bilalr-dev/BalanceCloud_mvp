// File Service based on Backend API Contract v1.0.0

import apiClient from './apiClient'
import { File as FileType, FileListResponse, StorageUsageResponse } from '@/types/api'

export const fileService = {
  async listFiles(parentId?: string): Promise<FileListResponse> {
    const params = parentId ? { parent_id: parentId } : {}
    const response = await apiClient.get<FileListResponse>('/files', { params })
    return response.data
  },

  async uploadFile(file: File, parentId?: string): Promise<FileType> {
    const formData = new FormData()
    formData.append('file', file)
    
    const params = parentId ? { parent_id: parentId } : {}
    const response = await apiClient.post<FileType>('/files/upload', formData, {
      params,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async downloadFile(fileId: string): Promise<Blob> {
    const response = await apiClient.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    })
    return response.data
  },

  async getStorageUsage(): Promise<StorageUsageResponse> {
    const response = await apiClient.get<StorageUsageResponse>('/files/storage/usage')
    return response.data
  },
}
