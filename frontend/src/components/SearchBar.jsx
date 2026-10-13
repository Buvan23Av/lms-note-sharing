/**
 * SearchBar.jsx - Unified Search Component
 * ==========================================
 * This is the single search box that triggers multi-database search.
 * 
 * When the user types and presses Enter:
 * 1. Navigates to /search?q=<query>
 * 2. SearchResults page calls GET /api/search?q=<query>
 * 3. Backend queries BOTH MongoDB and Neo4j
 * 4. Returns combined results
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * SearchBar component - renders search input and handles submission
 */
export default function SearchBar() {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()
  
  /**
   * Dispatches search query to the search results page route
   * @param {Event} e - Form submission event
   */
  const handleSearch = (e) => {
    e.preventDefault()
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`)
    }
  }
  
  return (
    <form onSubmit={handleSearch} className="search-bar">
      <input
        type="text"
        placeholder="Search notes, topics, subjects..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
      />
      <button type="submit" className="search-button">🔍</button>
    </form>
  )
}
