/**
 * App.jsx - Main Application Component
 * =====================================
 * Sets up routing and layout.
 * 
 * Pages:
 * - / : Dashboard (home)
 * - /search : Search results
 * - /notes/:id : Note detail view
 * - /login : Login page
 * - /register : Registration page
 * - /profile : Student profile
 */

import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import SearchResults from './pages/SearchResults'
import NoteDetail from './pages/NoteDetail'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import SearchBar from './components/SearchBar'

/**
 * Navbar - Top navigation bar component
 * @param {Object} props.student - Logged-in student object or null
 * @param {Function} props.onLogout - Callback function executed upon clicking logout
 */
function Navbar({ student, onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">📚</span>
          <span className="brand-text">LMS Notes</span>
        </Link>
        
        <div className="navbar-search">
          <SearchBar />
        </div>
        
        <div className="navbar-links">
          <Link to="/" className="nav-link">Dashboard</Link>
          {student ? (
            <>
              <Link to="/profile" className="nav-link">👤 {student.name}</Link>
              <button onClick={onLogout} className="nav-link btn-logout">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link btn-register">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

/**
 * AppContent - Internal layout containing routes and state management
 */
function AppContent() {
  const [student, setStudent] = useState(null)
  const navigate = useNavigate()
  
  useEffect(() => {
    // Check if user is logged in (token exists in local storage)
    const savedStudent = localStorage.getItem('student')
    if (savedStudent) {
      try {
        setStudent(JSON.parse(savedStudent))
      } catch {
        localStorage.removeItem('student')
      }
    }
  }, [])
  
  /**
   * Handle user login success
   * Stores session tokens and user state
   */
  const handleLogin = (studentData, token) => {
    setStudent(studentData)
    localStorage.setItem('student', JSON.stringify(studentData))
    localStorage.setItem('token', token)
    navigate('/')
  }
  
  /**
   * Handle user logout
   * Clears state and local storage keys
   */
  const handleLogout = () => {
    setStudent(null)
    localStorage.removeItem('student')
    localStorage.removeItem('token')
    navigate('/')
  }
  
  return (
    <div className="app">
      <Navbar student={student} onLogout={handleLogout} />
      
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard student={student} />} />
          <Route path="/search" element={<SearchResults student={student} />} />
          <Route path="/notes/:noteId" element={<NoteDetail student={student} />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register onLogin={handleLogin} />} />
          <Route path="/profile" element={<Profile student={student} />} />
        </Routes>
      </main>
      
      <footer className="footer">
        <p>LMS Note Sharing System — College Database Project</p>
        <p className="footer-tech">MongoDB + Neo4j + FastAPI + React</p>
      </footer>
    </div>
  )
}

/**
 * App - Root application with BrowserRouter wrapper
 */
export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}
