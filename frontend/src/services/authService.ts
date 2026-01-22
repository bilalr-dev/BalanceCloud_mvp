// Authentication Service based on Backend API Contract v1.0.0

import apiClient from './apiClient'
import { Token, User } from '@/types/api'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
}

export const authService = {
  async register(data: RegisterData): Promise<Token> {
    const response = await apiClient.post<Token>('/auth/register', data)
    return response.data
  },

  async login(credentials: LoginCredentials): Promise<Token> {
    const response = await apiClient.post<Token>('/auth/login', credentials)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },
}
