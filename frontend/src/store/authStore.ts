// Authentication Store using Zustand

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { User } from '@/types/api'
import { AUTH_TOKEN_KEY } from '@/config/api'
import { authService } from '@/services/authService'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchCurrentUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const tokenResponse = await authService.login({ email, password })
          const token = tokenResponse.access_token

          localStorage.setItem(AUTH_TOKEN_KEY, token)

          // Fetch user info
          const user = await authService.getCurrentUser()

          set({
            token,
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Incorrect email or password'
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            token: null,
            user: null,
          })
          throw error
        }
      },

      register: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const tokenResponse = await authService.register({ email, password })
          const token = tokenResponse.access_token

          localStorage.setItem(AUTH_TOKEN_KEY, token)

          // Fetch user info
          const user = await authService.getCurrentUser()

          set({
            token,
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Registration failed'
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            token: null,
            user: null,
          })
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem(AUTH_TOKEN_KEY)
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        })
      },

      fetchCurrentUser: async () => {
        set({ isLoading: true })
        try {
          const user = await authService.getCurrentUser()
          const token = localStorage.getItem(AUTH_TOKEN_KEY)
          set({
            user,
            token,
            isAuthenticated: !!token,
            isLoading: false,
            error: null,
          })
        } catch (error) {
          set({
            isLoading: false,
            isAuthenticated: false,
            user: null,
            token: null,
          })
        }
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
