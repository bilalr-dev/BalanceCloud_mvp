// Main Entry Point

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import '@/styles/globals.css'

// Initialize MSW in development (if needed)
async function enableMocking() {
  if (import.meta.env.MODE !== 'development') {
    return
  }

  // Check if MSW should be enabled
  const shouldMock = import.meta.env.VITE_USE_MOCK === 'true'
  if (!shouldMock) {
    return
  }

  const { worker } = await import('./mocks/browser')
  return worker.start({
    onUnhandledRequest: 'bypass',
  })
}

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  )
})
