/**
 * SearchResults.jsx - Unified Search Results Page
 * =================================================
 * THE MOST IMPORTANT PAGE FOR THE PROJECT DEMO!
 * 
 * This page demonstrates multi-database querying:
 * 1. User enters a search query
 * 2. ONE API call goes to the backend: GET /api/search?q=...
 * 3. Backend queries BOTH MongoDB (notes) AND Neo4j (relationships)
 * 4. Returns a COMBINED response
 * 5. This page displays:
 *    - Notes from MongoDB (with text search)
 *    - Related Topics from Neo4j (graph traversal)
 *    - Related Notes from Neo4j (graph connections)
 *    - Learning Path from Neo4j (prerequisite chain)
 */

import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import api from '../api'
import NoteCard from '../components/NoteCard'
import LearningPath from '../components/LearningPath'
import RelatedPanel from '../components/RelatedPanel'

/**
 * SearchResults - Handles multi-database search rendering MongoDB and Neo4j outputs
 * @param {Object} props.student - Current logged in student
 */
export default function SearchResults({ student }) {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    if (query) {
      performSearch(query)
    }
  }, [query])
  
  /**
   * Executes unified search call to backend
   * @param {string} searchQuery - Search keyword or topic
   */
  const performSearch = async (searchQuery) => {
    setLoading(true)
    setError(null)
    try {
      // ONE API call that queries BOTH databases!
      const response = await api.get(`/search?q=${encodeURIComponent(searchQuery)}`)
      setResults(response.data)
    } catch (err) {
      setError('Search failed. Please try again.')
      console.error('Search error:', err)
    } finally {
      setLoading(false)
    }
  }
  
  if (!query) {
    return (
      <div className="search-page">
        <h2>Enter a search query to find notes</h2>
        <p>Try: normalization, SQL, sorting, trees, deadlock</p>
      </div>
    )
  }
  
  if (loading) return <div className="loading">Searching both databases...</div>
  if (error) return <div className="error-message">{error}</div>
  if (!results) return null
  
  return (
    <div className="search-page">
      <div className="search-header">
        <h2>Search Results for "{results.query}"</h2>
        <div className="search-meta">
          <span className="db-badge mongo-badge">MongoDB: {results.notes.length} notes</span>
          <span className="db-badge neo4j-badge">Neo4j: {results.relatedTopics.length} topics, {results.relatedNotes.length} related</span>
        </div>
      </div>
      
      <div className="search-layout">
        {/* Main content: Notes from MongoDB */}
        <div className="search-main">
          <h3>📝 Notes (from MongoDB)</h3>
          {results.notes.length === 0 ? (
            <p className="no-results">No notes found matching your query.</p>
          ) : (
            <div className="notes-list">
              {results.notes.map(note => (
                <NoteCard 
                  key={note._id} 
                  note={note} 
                  student={student}
                />
              ))}
            </div>
          )}
        </div>
        
        {/* Sidebar: Related content from Neo4j */}
        <div className="search-sidebar">
          {/* Learning Path from Neo4j */}
          <LearningPath path={results.learningPath} />
          
          {/* Related Topics and Notes from Neo4j */}
          <RelatedPanel 
            relatedTopics={results.relatedTopics} 
            relatedNotes={results.relatedNotes} 
          />
          
          {/* Data source explanation */}
          <div className="data-source-info">
            <h4>ℹ️ How this works</h4>
            <p>
              <strong>One search, two databases!</strong><br/>
              Notes come from <em>MongoDB</em> (text search).<br/>
              Related topics and learning paths come from <em>Neo4j</em> (graph traversal).
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
