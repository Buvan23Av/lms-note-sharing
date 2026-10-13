/**
 * NoteCard.jsx - Note Display Card Component
 * ============================================
 * Reusable card component that displays a note's information.
 * Used in search results, dashboard, and profile pages.
 */

import React from 'react'
import { Link } from 'react-router-dom'
import api from '../api'

/**
 * NoteCard - Card component representing a single note item
 * @param {Object} props.note - Note object containing metadata
 * @param {Object} props.student - Current logged in student
 * @param {Function} props.onUpdate - Callback to trigger parent list refresh
 */
export default function NoteCard({ note, student, onUpdate }) {
  /**
   * Handles liking a note and refreshes stats
   * @param {Event} e - Click event
   */
  const handleLike = async (e) => {
    e.preventDefault()
    if (!student) {
      alert('Please login to like notes!')
      return
    }
    try {
      await api.post(`/notes/${note._id}/like?student_id=${student._id}`)
      if (onUpdate) onUpdate()
    } catch (err) {
      console.error('Like failed:', err)
    }
  }
  
  /**
   * Handles bookmarking a note into student's saved list
   * @param {Event} e - Click event
   */
  const handleBookmark = async (e) => {
    e.preventDefault()
    if (!student) {
      alert('Please login to bookmark notes!')
      return
    }
    try {
      await api.post(`/notes/${note._id}/bookmark?student_id=${student._id}`)
      alert('Bookmarked!')
    } catch (err) {
      console.error('Bookmark failed:', err)
    }
  }
  
  return (
    <div className="note-card">
      <Link to={`/notes/${note._id}`} className="note-card-link">
        <h3 className="note-title">{note.title}</h3>
        <p className="note-description">{note.description}</p>
        
        <div className="note-meta">
          <span className="note-subject">{note.subjectName || note.subject || ''}</span>
          <span className="note-topic">{note.topicName || note.topic || ''}</span>
        </div>
        
        <div className="note-tags">
          {note.tags && note.tags.map((tag, i) => (
            <span key={i} className="tag">{tag}</span>
          ))}
        </div>
      </Link>
      
      <div className="note-actions">
        <span className="note-uploader">📤 {note.uploaderName || note.uploader || 'Unknown'}</span>
        <button onClick={handleLike} className="action-btn like-btn" title="Like Note">
          ❤️ {note.likes || 0}
        </button>
        <button onClick={handleBookmark} className="action-btn bookmark-btn" title="Bookmark Note">
          🔖 Save
        </button>
      </div>
    </div>
  )
}
