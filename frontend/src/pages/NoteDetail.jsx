/**
 * NoteDetail.jsx - Note Detail Page
 * ===================================
 * Shows full details of a note:
 * - Note content from MongoDB
 * - Related notes from Neo4j
 * - Prerequisites from Neo4j
 * - Comments from MongoDB
 */

import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api'
import RelatedPanel from '../components/RelatedPanel'
import LearningPath from '../components/LearningPath'

/**
 * NoteDetail - Displays full note contents, metadata, prerequisites, and comment discussion
 * @param {Object} props.student - Logged-in student object
 */
export default function NoteDetail({ student }) {
  const { noteId } = useParams()
  const [note, setNote] = useState(null)
  const [prerequisites, setPrerequisites] = useState([])
  const [commentText, setCommentText] = useState('')
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadNote()
  }, [noteId])
  
  /**
   * Fetches note details from MongoDB and prerequisites from Neo4j
   */
  const loadNote = async () => {
    setLoading(true)
    try {
      const response = await api.get(`/notes/${noteId}`)
      setNote(response.data)
      
      // Get prerequisites from Neo4j graph traversal
      if (response.data.topicId) {
        try {
          const prereqRes = await api.get(`/graph/topic/${response.data.topicId}/prerequisites`)
          setPrerequisites(prereqRes.data.prerequisites || [])
        } catch {
          // Prerequisites are optional
        }
      }
    } catch (err) {
      console.error('Failed to load note:', err)
    } finally {
      setLoading(false)
    }
  }
  
  /**
   * Adds a new comment to the note via MongoDB
   * @param {Event} e - Form submission event
   */
  const handleComment = async (e) => {
    e.preventDefault()
    if (!student) {
      alert('Please login to comment!')
      return
    }
    if (!commentText.trim()) return
    
    try {
      await api.post(
        `/notes/${noteId}/comments?student_id=${student._id}&text=${encodeURIComponent(commentText)}`
      )
      setCommentText('')
      loadNote()  // Reload to show new comment
    } catch (err) {
      console.error('Comment failed:', err)
    }
  }
  
  /**
   * Likes the current note
   */
  const handleLike = async () => {
    if (!student) {
      alert('Please login to like!')
      return
    }
    try {
      await api.post(`/notes/${noteId}/like?student_id=${student._id}`)
      loadNote()
    } catch (err) {
      console.error('Like failed:', err)
    }
  }
  
  /**
   * Bookmarks the current note for the student
   */
  const handleBookmark = async () => {
    if (!student) {
      alert('Please login to bookmark!')
      return
    }
    try {
      await api.post(`/notes/${noteId}/bookmark?student_id=${student._id}`)
      alert('Bookmarked!')
    } catch (err) {
      console.error('Bookmark failed:', err)
    }
  }
  
  if (loading) return <div className="loading">Loading note...</div>
  if (!note) return <div className="error-message">Note not found</div>
  
  return (
    <div className="note-detail-page">
      <div className="note-detail-layout">
        {/* Main content */}
        <div className="note-detail-main">
          <div className="note-detail-header">
            <h1>{note.title}</h1>
            <div className="note-detail-meta">
              <span className="meta-item">📚 {note.subjectName}</span>
              <span className="meta-item">📌 {note.topicName}</span>
              <span className="meta-item">📤 {note.uploaderName}</span>
              <span className="meta-item">📅 {note.created_at ? new Date(note.created_at).toLocaleDateString() : ''}</span>
            </div>
          </div>
          
          <div className="note-detail-body">
            <p>{note.description}</p>
            
            <div className="note-tags">
              {note.tags && note.tags.map((tag, i) => (
                <Link key={i} to={`/search?q=${tag}`} className="tag">{tag}</Link>
              ))}
            </div>
            
            {note.fileUrl && (
              <a href={note.fileUrl} className="download-btn" target="_blank" rel="noopener">
                📥 Download File
              </a>
            )}
          </div>
          
          <div className="note-detail-actions">
            <button onClick={handleLike} className="action-btn like-btn">❤️ Like ({note.likes || 0})</button>
            <button onClick={handleBookmark} className="action-btn bookmark-btn">🔖 Bookmark</button>
          </div>
          
          {/* Comments Section */}
          <div className="comments-section">
            <h3>💬 Comments ({note.comments?.length || 0})</h3>
            
            <form onSubmit={handleComment} className="comment-form">
              <textarea
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder={student ? "Write a comment..." : "Login to comment"}
                disabled={!student}
                className="comment-input"
              />
              <button type="submit" className="comment-submit" disabled={!student}>
                Post Comment
              </button>
            </form>
            
            <div className="comments-list">
              {note.comments && note.comments.map(comment => (
                <div key={comment._id} className="comment">
                  <div className="comment-header">
                    <strong>{comment.studentName}</strong>
                    <span className="comment-date">
                      {comment.created_at ? new Date(comment.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                  <p>{comment.text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Sidebar with Neo4j data */}
        <div className="note-detail-sidebar">
          {/* Prerequisites from Neo4j */}
          {prerequisites.length > 0 && (
            <div className="prerequisite-panel">
              <h3>📋 Prerequisites</h3>
              <p className="prereq-hint">Learn these topics first:</p>
              <ul className="prereq-list">
                {prerequisites.map((prereq, i) => (
                  <li key={prereq.id || i} className="prereq-item">
                    {prereq.name}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Related Notes from Neo4j */}
          <RelatedPanel 
            relatedTopics={[]} 
            relatedNotes={note.relatedNotes || []} 
          />
        </div>
      </div>
    </div>
  )
}
