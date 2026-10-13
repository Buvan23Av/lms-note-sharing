/**
 * Profile.jsx - Student Profile Page
 * ===================================
 * Displays current student info, Neo4j graph relationships (following, followers, topics),
 * uploaded notes, and MongoDB bookmarks.
 */

import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'

/**
 * Profile page component
 * @param {Object} props.student - Logged in student object
 */
export default function Profile({ student }) {
  const [connections, setConnections] = useState(null)
  const [bookmarks, setBookmarks] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  
  useEffect(() => {
    if (!student) {
      navigate('/login')
      return
    }
    loadProfile()
  }, [student])
  
  /**
   * Loads student connections from Neo4j graph and bookmarks from MongoDB
   */
  const loadProfile = async () => {
    setLoading(true)
    try {
      const [connRes, bmRes] = await Promise.allSettled([
        api.get(`/graph/student/${student._id}/connections`),
        api.get(`/students/${student._id}/bookmarks`)
      ])
      
      if (connRes.status === 'fulfilled') setConnections(connRes.value.data)
      if (bmRes.status === 'fulfilled') setBookmarks(bmRes.value.data)
    } catch (err) {
      console.error('Failed to load profile data:', err)
    } finally {
      setLoading(false)
    }
  }
  
  if (!student) return null
  if (loading) return <div className="loading">Loading profile...</div>
  
  return (
    <div className="profile-page">
      <div className="profile-header">
        <div className="profile-avatar">👤</div>
        <h2>{student.name}</h2>
        <p>{student.department} • Semester {student.semester}</p>
        <p className="profile-email">{student.email}</p>
      </div>
      
      <div className="profile-grid">
        {/* Topics Studying (from Neo4j) */}
        {connections?.topics && (
          <div className="profile-section">
            <h3>📌 Topics Studying</h3>
            <ul className="profile-list">
              {connections.topics.map((t, i) => (
                <li key={i}>{t.name} <span className="text-muted">({t.subject})</span></li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Uploaded Notes (from Neo4j) */}
        {connections?.uploaded && (
          <div className="profile-section">
            <h3>📤 My Uploads</h3>
            <ul className="profile-list">
              {connections.uploaded.map((n, i) => (
                <li key={i}><Link to={`/notes/${n.id}`}>{n.title}</Link></li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Following (from Neo4j) */}
        {connections?.following && (
          <div className="profile-section">
            <h3>👥 Following</h3>
            <ul className="profile-list">
              {connections.following.map((f, i) => (
                <li key={i}>{f.name}</li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Followers (from Neo4j) */}
        {connections?.followers && (
          <div className="profile-section">
            <h3>👥 Followers</h3>
            <ul className="profile-list">
              {connections.followers.map((f, i) => (
                <li key={i}>{f.name}</li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Bookmarks (from MongoDB) */}
        {bookmarks.length > 0 && (
          <div className="profile-section">
            <h3>🔖 Bookmarked Notes</h3>
            <ul className="profile-list">
              {bookmarks.map((note, i) => (
                <li key={i}><Link to={`/notes/${note._id}`}>{note.title}</Link></li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
