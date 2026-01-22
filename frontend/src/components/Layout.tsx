// Layout Component with Navigation

import { ReactNode } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout, isAuthenticated } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (!isAuthenticated) {
    return <>{children}</>
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-container">
          <Link to="/" className="navbar-brand">
            <span className="navbar-logo">☁️</span>
            <span className="navbar-title">BalanceCloud</span>
          </Link>
          
          <div className="navbar-menu">
            <Link
              to="/"
              className={`navbar-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              Files
            </Link>
            <Link
              to="/cloud-accounts"
              className={`navbar-link ${location.pathname === '/cloud-accounts' ? 'active' : ''}`}
            >
              Cloud Accounts
            </Link>
          </div>

          <div className="navbar-user">
            <span className="navbar-email">{user?.email}</span>
            <button onClick={handleLogout} className="btn btn-outline btn-sm">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="main-content">
        {children}
      </main>
    </div>
  )
}
