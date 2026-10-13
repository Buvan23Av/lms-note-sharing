/**
 * api.js - API Client
 * ====================
 * Centralized HTTP client for communicating with the FastAPI backend.
 * All API calls go through this file.
 * 
 * The frontend NEVER connects directly to MongoDB or Neo4j!
 * It always goes through the FastAPI backend.
 */

import axios from 'axios'

// Create an axios instance with base configuration
const api = axios.create({
  baseURL: '/api',  // Vite proxy forwards /api to http://localhost:8000/api
  timeout: 10000,    // 10 second timeout
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to every request (if logged in)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('student')
    }
    return Promise.reject(error)
  }
)

export default api
