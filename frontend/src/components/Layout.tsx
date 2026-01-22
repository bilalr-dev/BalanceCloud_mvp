// Layout Component with Sidebar Navigation

import { ReactNode } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import ThemeToggle from './ThemeToggle'

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

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/files', label: 'Files', icon: '📁' },
    { path: '/cloud-accounts', label: 'Connected Accounts', icon: '☁️' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Top Header */}
      <header className="sticky top-0 z-50 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">☁️</span>
                <span className="text-xl font-bold text-gray-900 dark:text-white">BalanceCloud</span>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="Search files..."
                  className="bg-transparent border-none outline-none text-sm text-gray-600 dark:text-gray-300 w-48"
                />
              </div>
              
              <ThemeToggle />
              
              <div className="flex items-center gap-3">
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.email}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="hidden lg:flex flex-col w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 min-h-[calc(100vh-4rem)]">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">BalanceCloud MVP</p>
          </div>
          
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-gray-500 dark:text-gray-400">All systems operational</span>
            </div>
          </div>
        </aside>

        {/* Mobile Sidebar Toggle */}
        <div className="lg:hidden fixed bottom-4 left-4 z-40">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2">
            <div className="flex flex-col gap-2">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`p-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <span className="text-xl">{item.icon}</span>
                  </Link>
                )
              })}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="flex-1 lg:ml-0">
          <div className="p-4 sm:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
