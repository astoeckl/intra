/**
 * Application Entry Point
 *
 * Bootstraps the React application with required providers:
 * - React Query for server state management
 * - Strict Mode for development warnings
 *
 * @module main
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'

/**
 * React Query client instance with default configuration.
 *
 * Default options:
 * - staleTime: 5 minutes - data considered fresh for 5 minutes before refetching
 * - retry: 1 - retry failed requests once before showing error
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
