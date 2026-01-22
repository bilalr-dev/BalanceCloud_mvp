import apiClient from './apiClient'

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

export interface FileListResponse {
  files: File[]
  total: number
}

export const fileService = {
  listFiles: async (parentId?: string): Promise<FileListResponse> => {
    const params = parentId ? { parent_id: parentId } : {}
    const response = await apiClient.get<FileListResponse>('/files', { params })
    return response.data
  },

  uploadFile: async (file: File, parentId?: string): Promise<File> => {
    const formData = new FormData()
    formData.append('file', file)
    if (parentId) {
      formData.append('parent_id', parentId)
    }
    const response = await apiClient.post<File>('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  downloadFile: async (fileId: string): Promise<Blob> => {
    const response = await apiClient.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    })
    return response.data
  },

  deleteFile: async (fileId: string): Promise<void> => {
    await apiClient.delete(`/files/${fileId}`)
  },

  createFolder: async (name: string, parentId?: string): Promise<File> => {
    const data: any = { name, is_folder: true }
    if (parentId) {
      data.parent_id = parentId
    }
    const response = await apiClient.post<File>('/files', data)
    return response.data
  },
}
