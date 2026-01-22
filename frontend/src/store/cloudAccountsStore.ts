// Cloud Accounts Store using Zustand

import { create } from 'zustand'
import { CloudAccount, CloudProvider } from '@/types/api'
import { cloudAccountService } from '@/services/cloudAccountService'

interface CloudAccountsState {
  accounts: CloudAccount[]
  isLoading: boolean
  error: string | null
  fetchAccounts: () => Promise<void>
  disconnectAccount: (accountId: string) => Promise<void>
  clearError: () => void
}

export const useCloudAccountsStore = create<CloudAccountsState>((set, get) => ({
  accounts: [],
  isLoading: false,
  error: null,

  fetchAccounts: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await cloudAccountService.listAccounts()
      set({
        accounts: response.accounts,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch cloud accounts'
      set({
        isLoading: false,
        error: errorMessage,
      })
    }
  },

  disconnectAccount: async (accountId: string) => {
    set({ isLoading: true, error: null })
    try {
      await cloudAccountService.disconnectAccount(accountId)
      // Remove account from list
      set((state) => ({
        accounts: state.accounts.filter((acc) => acc.id !== accountId),
        isLoading: false,
        error: null,
      }))
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to disconnect account'
      set({
        isLoading: false,
        error: errorMessage,
      })
      throw error
    }
  },

  clearError: () => {
    set({ error: null })
  },
}))
