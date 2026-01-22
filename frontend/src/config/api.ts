// API Configuration based on Frontend-Backend Contract v1.0.0

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const AUTH_TOKEN_KEY = 'auth_token'

// Token expiration: 30 minutes (as per contract)
export const TOKEN_EXPIRATION_MS = 30 * 60 * 1000
