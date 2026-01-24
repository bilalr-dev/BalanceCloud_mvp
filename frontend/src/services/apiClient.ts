// API Client based on Frontend-Backend Contract v1.0.0

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { API_BASE_URL, AUTH_TOKEN_KEY } from '@/config/api'
import { ErrorResponse } from '@/types/api'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle errors (401, 429 rate limiting)
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    if (error.response?.status === 401) {
      // Clear token from localStorage
      localStorage.removeItem(AUTH_TOKEN_KEY)
      // Clear Zustand persisted auth state
      localStorage.removeItem('auth-storage')
      // Only redirect if not already on login/register page
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login'
      }
    }
    
    // Handle rate limiting - don't spam errors, just log
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || '60'
      console.warn(`Rate limit exceeded. Retry after ${retryAfter} seconds`)
      // Don't throw error for rate limits on storage usage - it's not critical
      if (error.config?.url?.includes('/storage/usage')) {
        return Promise.resolve({ data: null, status: 429 } as any)
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
