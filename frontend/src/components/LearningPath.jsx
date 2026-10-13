/**
 * LearningPath.jsx - Learning Path Visualization
 * ================================================
 * Displays the prerequisite learning path from Neo4j.
 * Shows: Topic A → Topic B → Topic C
 */

import React from 'react'

/**
 * LearningPath - Renders an ordered sequence of topic prerequisites
 * @param {Array<string>} props.path - Array of topic names representing prerequisite order
 */
export default function LearningPath({ path }) {
  if (!path || path.length === 0) return null
  
  return (
    <div className="learning-path">
      <h3>📖 Learning Path</h3>
      <div className="path-container">
        {path.map((topic, index) => (
          <React.Fragment key={index}>
            <div className="path-node">
              <span className="path-number">{index + 1}</span>
              <span className="path-name">{topic}</span>
            </div>
            {index < path.length - 1 && (
              <div className="path-arrow">→</div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}
