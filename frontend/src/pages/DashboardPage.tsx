import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authService } from '../services/authService'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, token } = useAuthStore()

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }

    // Verify token is still valid and fetch user data
    authService
      .getCurrentUser()
      .then((userData) => {
        useAuthStore.getState().setAuth(token, {
          id: userData.id,
          email: userData.email,
        })
      })
      .catch(() => {
        navigate('/login')
      })
  }, [token, navigate])

  if (!user) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">BalanceCloud MVP</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">{user.email}</span>
              <button
                onClick={() => {
                  useAuthStore.getState().clearAuth()
                  navigate('/login')
                }}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome, {user.email}!</h2>
          <p className="text-gray-600 mb-6">
            Manage your files and cloud storage accounts from here.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => navigate('/files')}
              className="p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">📁 Files</h3>
              <p className="text-gray-600">Manage your files and folders</p>
            </button>

            <button
              onClick={() => navigate('/cloud-accounts')}
              className="p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">☁️ Cloud Accounts</h3>
              <p className="text-gray-600">Connect Google Drive or OneDrive</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
