import { create } from 'zustand'
import { CloudAccount } from '../services/cloudAccountService'

interface CloudAccountsState {
  accounts: CloudAccount[]
  loading: boolean
  error: string | null
  setAccounts: (accounts: CloudAccount[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  addAccount: (account: CloudAccount) => void
  removeAccount: (accountId: string) => void
}

export const useCloudAccountsStore = create<CloudAccountsState>((set) => ({
  accounts: [],
  loading: false,
  error: null,
  setAccounts: (accounts) => set({ accounts }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  addAccount: (account) =>
    set((state) => ({
      accounts: [...state.accounts.filter((a) => a.id !== account.id), account],
    })),
  removeAccount: (accountId) =>
    set((state) => ({
      accounts: state.accounts.filter((a) => a.id !== accountId),
    })),
}))
