/**
 * API Client Configuration.
 *
 * Provides a configured Axios instance with authentication
 * and error handling interceptors.
 */

import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Pre-configured Axios instance for API requests.
 *
 * Automatically includes authorization headers when token is present
 * and handles 401 responses by redirecting to login.
 */
export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT token to all requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle authentication errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * Verify API connectivity.
 * @returns Health check response from backend.
 */
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}
