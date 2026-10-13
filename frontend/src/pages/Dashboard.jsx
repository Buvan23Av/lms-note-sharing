/**
 * Dashboard.jsx - Home Page / Dashboard
 * =======================================
 * Shows overview of the LMS:
 * - Statistics (from Neo4j)
 * - Recent/popular notes (from MongoDB)
 * - Subject navigation (from Neo4j)
 * - Recommendations (if logged in, from Neo4j)
 */

import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import NoteCard from '../components/NoteCard'

/**
 * Dashboard - Displays high-level system statistics, subjects, recommendations, and recent notes
 * @param {Object} props.student - Logged in student info
 */
export default function Dashboard({ student }) {
  const [notes, setNotes] = useState([])
  const [stats, setStats] = useState(null)
  const [subjects, setSubjects] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    loadDashboard()
  }, [student])
  
  /**
   * Loads dashboard metrics, subjects list, notes, and personalized recommendations
   */
  const loadDashboard = async () => {
    setLoading(true)
    setError(null)
    try {
      // Fetch data in parallel from MongoDB and Neo4j endpoints
      const [notesRes, statsRes, subjectsRes] = await Promise.allSettled([
        api.get('/notes?limit=12'),
        api.get('/dashboard/stats'),
        api.get('/subjects')
      ])
      
      if (notesRes.status === 'fulfilled') setNotes(notesRes.value.data)
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data)
      if (subjectsRes.status === 'fulfilled') setSubjects(subjectsRes.value.data)
      
      // Get recommendations if logged in (from Neo4j collaborative filtering)
      if (student) {
        try {
          const recRes = await api.get(`/graph/student/${student._id}/recommendations`)
          setRecommendations(recRes.data.recommendations || [])
        } catch {
          // Recommendations are optional
        }
      }
    } catch (err) {
      setError('Failed to load dashboard. Are the databases running?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) return <div className="loading">Loading dashboard...</div>
  if (error) return <div className="error-message">{error}</div>
  
  return (
    <div className="dashboard">
      {/* Stats Section */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-icon">📝</span>
            <span className="stat-number">{stats.notes || 0}</span>
            <span className="stat-label">Notes</span>
          </div>
          <div className="stat-card">
            <span className="stat-icon">📚</span>
            <span className="stat-number">{stats.subjects || 0}</span>
            <span className="stat-label">Subjects</span>
          </div>
          <div className="stat-card">
            <span className="stat-icon">📌</span>
            <span className="stat-number">{stats.topics || 0}</span>
            <span className="stat-label">Topics</span>
          </div>
          <div className="stat-card">
            <span className="stat-icon">👨‍🎓</span>
            <span className="stat-number">{stats.students || 0}</span>
            <span className="stat-label">Students</span>
          </div>
        </div>
      )}
      
      {/* Subject Filters */}
      <section className="section">
        <h2 className="section-title">Browse by Subject</h2>
        <div className="subject-chips">
          {subjects.map(subject => (
            <Link 
              key={subject._id} 
              to={`/search?q=${encodeURIComponent(subject.name)}`}
              className="subject-chip"
            >
              {subject.name}
            </Link>
          ))}
        </div>
      </section>
      
      {/* Recommendations (only if logged in) */}
      {student && recommendations.length > 0 && (
        <section className="section">
          <h2 className="section-title">✨ Recommended for You</h2>
          <div className="recommendation-list">
            {recommendations.map((rec, i) => (
              <Link key={rec.id || i} to={`/notes/${rec.id}`} className="rec-card">
                <h4>{rec.title}</h4>
                <p>Topic: {rec.topic} • By: {rec.uploader}</p>
              </Link>
            ))}
          </div>
        </section>
      )}
      
      {/* Recent Notes */}
      <section className="section">
        <h2 className="section-title">Recent Notes</h2>
        <div className="notes-grid">
          {notes.map(note => (
            <NoteCard 
              key={note._id} 
              note={note} 
              student={student}
              onUpdate={loadDashboard}
            />
          ))}
        </div>
      </section>
    </div>
  )
}
