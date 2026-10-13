/**
 * Login.jsx - User Authentication Page
 * =====================================
 * Allows students to log in using their college email and password.
 */

import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

/**
 * Login page component
 * @param {Function} props.onLogin - Callback invoked upon successful authentication
 */
export default function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  /**
   * Submits credentials to FastAPI backend /students/login
   * @param {Event} e - Form event
   */
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    
    try {
      const response = await api.post('/students/login', { email, password })
      onLogin(response.data.student, response.data.access_token)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Welcome Back 👋</h2>
        <p className="auth-subtitle">Login to your account</p>
        
        {error && <div className="auth-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@college.edu"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>
          
          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <p className="auth-link">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
        
        <div className="demo-credentials">
          <h4>Demo Credentials:</h4>
          <p>Email: arun@college.edu</p>
          <p>Password: password123</p>
        </div>
      </div>
    </div>
  )
}
