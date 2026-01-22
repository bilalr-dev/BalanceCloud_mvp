// Main Entry Point

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import '@/styles/globals.css'

// Initialize theme immediately
const storedTheme = localStorage.getItem('theme') || 'dark'
const root = document.documentElement
root.classList.remove('light', 'dark')
root.classList.add(storedTheme)

// Initialize MSW in development (if needed)
// MSW is optional and only loads if VITE_USE_MOCK=true
async function enableMocking() {
  if (import.meta.env.MODE !== 'development') {
    return
  }

  // Check if MSW should be enabled
  const shouldMock = import.meta.env.VITE_USE_MOCK === 'true'
  if (!shouldMock) {
    return
  }

  // Dynamically import MSW only when needed
  try {
    const mswModule = await import('msw')
    const { handlers } = await import('./mocks/handlers')
    
    if (mswModule.setupWorker) {
      const worker = mswModule.setupWorker(...handlers)
      return worker.start({
        onUnhandledRequest: 'bypass',
      })
    }
  } catch (error) {
    console.warn('MSW not available, skipping mock setup:', error)
  }
}

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  )
})
