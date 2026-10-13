/**
 * RelatedPanel.jsx - Related Content Panel
 * ==========================================
 * Shows related topics and notes from Neo4j graph traversal.
 * Used in search results and note detail pages.
 */

import React from 'react'
import { Link } from 'react-router-dom'

/**
 * RelatedPanel - Displays related topics and notes discovered from graph connections
 * @param {Array} props.relatedTopics - List of topic objects with id, name, subject
 * @param {Array} props.relatedNotes - List of note objects with id, title
 */
export default function RelatedPanel({ relatedTopics, relatedNotes }) {
  const hasTopics = relatedTopics && relatedTopics.length > 0
  const hasNotes = relatedNotes && relatedNotes.length > 0
  
  if (!hasTopics && !hasNotes) return null
  
  return (
    <div className="related-panel">
      {hasTopics && (
        <div className="related-section">
          <h3>🔗 Related Topics</h3>
          <ul className="related-list">
            {relatedTopics.map((topic, i) => (
              <li key={topic.id || i} className="related-item">
                <span className="related-name">{topic.name}</span>
                {topic.subject && (
                  <span className="related-subject">{topic.subject}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {hasNotes && (
        <div className="related-section">
          <h3>📄 Related Notes</h3>
          <ul className="related-list">
            {relatedNotes.map((note, i) => (
              <li key={note.id || i} className="related-item">
                <Link to={`/notes/${note.id}`} className="related-link">
                  {note.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
