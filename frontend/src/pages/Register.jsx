/**
 * Register.jsx - Student Registration Page
 * ==========================================
 * Allows new students to create an account in the LMS.
 */

import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

/**
 * Register page component
 * @param {Function} props.onLogin - Callback invoked upon successful registration & login
 */
export default function Register({ onLogin }) {
  const [form, setForm] = useState({
    name: '', email: '', password: '', department: 'CSE', semester: 1
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  /**
   * Handle changes across form fields
   * @param {Event} e - Input change event
   */
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }
  
  /**
   * Submits new student registration payload to /students/register
   * @param {Event} e - Form event
   */
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    
    try {
      const payload = { ...form, semester: parseInt(form.semester) }
      const response = await api.post('/students/register', payload)
      onLogin(response.data.student, response.data.access_token)
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Create Account 🎓</h2>
        <p className="auth-subtitle">Join the note sharing community</p>
        
        {error && <div className="auth-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input name="name" value={form.name} onChange={handleChange} placeholder="Your name" required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="your@college.edu" required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input name="password" type="password" value={form.password} onChange={handleChange} placeholder="Min 6 characters" required minLength={6} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Department</label>
              <select name="department" value={form.department} onChange={handleChange}>
                <option value="CSE">CSE</option>
                <option value="ECE">ECE</option>
                <option value="MECH">MECH</option>
                <option value="EEE">EEE</option>
                <option value="CIVIL">CIVIL</option>
              </select>
            </div>
            <div className="form-group">
              <label>Semester</label>
              <select name="semester" value={form.semester} onChange={handleChange}>
                {[1,2,3,4,5,6,7,8].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Creating...' : 'Register'}
          </button>
        </form>
        
        <p className="auth-link">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}
