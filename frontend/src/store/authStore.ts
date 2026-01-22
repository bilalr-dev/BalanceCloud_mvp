import { create } from 'zustand'

interface User {
  id: string
  email: string
}

interface AuthState {
  token: string | null
  user: User | null
  setAuth: (token: string, user: User) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('auth_token'),
  user: null,
  setAuth: (token: string, user: User) => {
    localStorage.setItem('auth_token', token)
    set({ token, user })
  },
  clearAuth: () => {
    localStorage.removeItem('auth_token')
    set({ token: null, user: null })
  },
}))
