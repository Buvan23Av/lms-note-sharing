"""
search.py - Search API Routes
===============================
Handles the unified search endpoint that queries both MongoDB and Neo4j.

This is the MOST IMPORTANT route for the project demonstration!

Endpoint: GET /api/search?q=normalization
- Receives a search query from the frontend
- Calls the search service which queries BOTH databases
- Returns one combined JSON response
"""

from fastapi import APIRouter, Query, HTTPException
from app.services.search_service import (
    unified_search, 
    search_notes_by_subject, 
    search_notes_by_topic
)
from app.services.graph_service import (
    get_notes_for_topic,
    get_notes_by_followed,
    get_related_notes,
    get_prerequisites,
    recommend_notes,
    shortest_path_between_topics,
    get_student_connections,
    get_dashboard_stats,
    get_subject_topic_tree
)

router = APIRouter()


@router.get("/search")
def search(q: str = Query(..., min_length=1, description="Search query text")):
    """
    🔍 UNIFIED SEARCH - Queries both MongoDB AND Neo4j!
    
    This is the KEY endpoint for the project.
    
    Flow:
    1. React sends: GET /api/search?q=normalization
    2. Backend queries MongoDB (text search for notes)
    3. Backend queries Neo4j (related topics, notes, learning path)
    4. Backend combines results using shared IDs
    5. Returns ONE JSON response with all data
    
    Try in Swagger UI: http://localhost:8000/docs
    """
    try:
        result = unified_search(q)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search/subject/{subject_id}")
def search_by_subject(subject_id: str):
    """Get all notes for a specific subject."""
    try:
        notes = search_notes_by_subject(subject_id)
        return {"subjectId": subject_id, "notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/topic/{topic_id}")
def search_by_topic(topic_id: str):
    """Get all notes for a specific topic."""
    try:
        notes = search_notes_by_topic(topic_id)
        return {"topicId": topic_id, "notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# GRAPH QUERY ENDPOINTS
# ============================================

@router.get("/graph/topic/{topic_id}/notes")
def graph_topic_notes(topic_id: str):
    """
    USE CASE A: Find all notes about a topic (Neo4j query).
    """
    try:
        return {"topicId": topic_id, "notes": get_notes_for_topic(topic_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/student/{student_id}/feed")
def graph_followed_notes(student_id: str):
    """
    USE CASE B: Notes uploaded by students the user follows.
    """
    try:
        return {"studentId": student_id, "notes": get_notes_by_followed(student_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/note/{note_id}/related")
def graph_related_notes(note_id: str):
    """
    USE CASE C: Find notes related to the currently opened note.
    """
    try:
        return {"noteId": note_id, "relatedNotes": get_related_notes(note_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/topic/{topic_id}/prerequisites")
def graph_prerequisites(topic_id: str):
    """
    USE CASE D: Find prerequisite topics for a given topic.
    Shows the learning path: "Learn A → B → C before this topic"
    """
    try:
        return {"topicId": topic_id, "prerequisites": get_prerequisites(topic_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/student/{student_id}/recommendations")
def graph_recommendations(student_id: str):
    """
    USE CASE E: Recommend notes based on student's study topics and bookmarks.
    """
    try:
        return {"studentId": student_id, "recommendations": recommend_notes(student_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/path/{topic_id_1}/{topic_id_2}")
def graph_shortest_path(topic_id_1: str, topic_id_2: str):
    """
    USE CASE F: Find shortest path between two topics.
    """
    try:
        return shortest_path_between_topics(topic_id_1, topic_id_2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/student/{student_id}/connections")
def graph_student_connections(student_id: str):
    """
    Get a student's complete learning network from Neo4j.
    """
    try:
        return get_student_connections(student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/stats")
def dashboard_stats():
    """Get overview statistics for the dashboard."""
    try:
        return get_dashboard_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/subjects")
def dashboard_subjects():
    """Get subject → topic → note count tree for navigation."""
    try:
        return get_subject_topic_tree()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
