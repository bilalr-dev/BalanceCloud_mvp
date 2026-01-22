import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useCloudAccountsStore } from '../store/cloudAccountsStore'
import { cloudAccountService } from '../services/cloudAccountService'

export default function OAuthCallbackPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { addAccount, setError } = useCloudAccountsStore()

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')
      const provider = window.location.pathname.includes('google')
        ? 'google_drive'
        : 'onedrive'

      if (error) {
        setError(`OAuth error: ${error}`)
        navigate('/cloud-accounts')
        return
      }

      if (!code || !state) {
        setError('Missing OAuth parameters')
        navigate('/cloud-accounts')
        return
      }

      // Verify state
      const storedState = sessionStorage.getItem(`oauth_state_${provider}`)
      if (state !== storedState) {
        setError('Invalid OAuth state')
        navigate('/cloud-accounts')
        return
      }

      try {
        const response = await cloudAccountService.handleCallback(provider, code, state)
        addAccount(response as any)
        sessionStorage.removeItem(`oauth_state_${provider}`)
        navigate('/cloud-accounts')
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to complete OAuth flow')
        navigate('/cloud-accounts')
      }
    }

    handleCallback()
  }, [searchParams, navigate, addAccount, setError])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Completing OAuth connection...</p>
      </div>
    </div>
  )
}
