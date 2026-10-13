"""
search_service.py - Unified Multi-Database Search Service
==========================================================
This is the HEART of the multi-database integration!

How unified search works:
1. User types a search query (e.g., 'normalization')
2. Frontend sends ONE request to the API
3. This service queries BOTH databases:
   - MongoDB: text search on note titles, descriptions, and tags
   - Neo4j: graph traversal for related topics, notes, and learning paths
4. Results are COMBINED using shared entity IDs
5. ONE unified JSON response is returned

Why use two databases?
- MongoDB excels at: full-text search, storing document details, filtering
- Neo4j excels at: finding relationships, recommendations, learning paths
- Together: you get BOTH detailed content AND relationship insights!
"""

from typing import List, Dict, Any
from app.database.mongodb import get_db
from app.database.neo4j_db import run_query


def unified_search(query: str) -> dict:
    """
    Execute a unified search across MongoDB and Neo4j.
    
    This is the KEY function for the college project demo!
    
    Steps:
    1. Search MongoDB for notes matching the query text
    2. Get topic IDs from the matching notes
    3. Query Neo4j for related topics using graph traversal
    4. Query Neo4j for related notes through graph connections
    5. Query Neo4j for learning path (prerequisite chain)
    6. Combine everything into one response
    
    Args:
        query: The search text from the user
    
    Returns:
        Dictionary with notes, relatedTopics, relatedNotes, and learningPath
    """
    result = {
        "query": query,
        "notes": [],
        "relatedTopics": [],
        "relatedNotes": [],
        "learningPath": []
    }
    
    # ============================================
    # STEP 1: Search MongoDB for matching notes
    # ============================================
    # MongoDB's $text operator searches the text index we created on
    # title, description, and tags fields
    try:
        db = get_db()
        
        # Use MongoDB text search
        # The $text operator searches the text index
        # $meta: "textScore" sorts results by relevance
        mongo_notes = list(db["notes"].find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(20))
        
        # If text search returns nothing, fall back to regex search
        if not mongo_notes:
            regex_pattern = {"$regex": query, "$options": "i"}  # case-insensitive
            mongo_notes = list(db["notes"].find({
                "$or": [
                    {"title": regex_pattern},
                    {"description": regex_pattern},
                    {"tags": regex_pattern}
                ]
            }).limit(20))
        
        # Enrich notes with uploader name, subject name, topic name
        # This is called "manual joining" since MongoDB doesn't have JOINs like SQL
        for note in mongo_notes:
            # Look up the student who uploaded this note
            student = db["students"].find_one({"_id": note.get("uploadedBy")})
            note["uploaderName"] = student["name"] if student else "Unknown"
            
            # Look up the subject
            subject = db["subjects"].find_one({"_id": note.get("subjectId")})
            note["subjectName"] = subject["name"] if subject else "Unknown"
            
            # Look up the topic
            topic = db["topics"].find_one({"_id": note.get("topicId")})
            note["topicName"] = topic["name"] if topic else "Unknown"
            
            # Remove MongoDB internal score field if present
            note.pop("score", None)
            
            # Convert _id to string for JSON serialization
            note["_id"] = str(note["_id"])
            
            result["notes"].append(note)
        
    except Exception as e:
        print(f"MongoDB search error: {e}")
        # Continue to Neo4j even if MongoDB fails
    
    # ============================================
    # STEP 2: Query Neo4j for related topics
    # ============================================
    # Find topics that are connected to the search query through:
    # - Direct name match
    # - Notes that mention the topic
    # - Prerequisites and related topics
    try:
        # Find topics matching the query name
        related_topics = run_query(
            """
            MATCH (t:Topic)
            WHERE toLower(t.name) CONTAINS toLower($query)
            OPTIONAL MATCH (t)-[:PART_OF]->(s:Subject)
            RETURN t.topicId AS id, t.name AS name, 
                   s.name AS subject, s.subjectId AS subjectId
            LIMIT 10
            """,
            {"query": query}
        )
        result["relatedTopics"] = related_topics
        
        # Also find topics related to the matched notes through graph traversal
        # Get topic IDs from MongoDB results to find connected topics in Neo4j
        topic_ids = list(set(
            note.get("topicId", "") for note in result["notes"] if note.get("topicId")
        ))
        
        if topic_ids:
            # Find neighboring topics in the graph
            neighbor_topics = run_query(
                """
                MATCH (t:Topic)
                WHERE t.topicId IN $topicIds
                MATCH (t)-[:PREREQUISITE_OF|PART_OF*1..2]-(related:Topic)
                WHERE NOT related.topicId IN $topicIds
                OPTIONAL MATCH (related)-[:PART_OF]->(s:Subject)
                RETURN DISTINCT related.topicId AS id, related.name AS name,
                       s.name AS subject
                LIMIT 10
                """,
                {"topicIds": topic_ids}
            )
            
            # Add neighbor topics that aren't already in the list
            existing_ids = {t["id"] for t in result["relatedTopics"]}
            for topic in neighbor_topics:
                if topic["id"] not in existing_ids:
                    result["relatedTopics"].append(topic)
    
    except Exception as e:
        print(f"Neo4j topic search error: {e}")
    
    # ============================================
    # STEP 3: Query Neo4j for related notes
    # ============================================
    # Find notes that are related through the graph:
    # - Directly connected via RELATED_TO
    # - Notes about the same or related topics
    try:
        note_ids = [note["_id"] for note in result["notes"]]
        
        if note_ids:
            related_notes = run_query(
                """
                MATCH (n:Note)
                WHERE n.noteId IN $noteIds
                MATCH (n)-[:RELATED_TO|ABOUT*1..2]-(related:Note)
                WHERE NOT related.noteId IN $noteIds
                RETURN DISTINCT related.noteId AS id, related.title AS title
                LIMIT 10
                """,
                {"noteIds": note_ids}
            )
            result["relatedNotes"] = related_notes
        else:
            # If no notes found, try to find notes about matching topics
            related_notes = run_query(
                """
                MATCH (t:Topic)
                WHERE toLower(t.name) CONTAINS toLower($query)
                MATCH (n:Note)-[:ABOUT]->(t)
                RETURN DISTINCT n.noteId AS id, n.title AS title
                LIMIT 10
                """,
                {"query": query}
            )
            result["relatedNotes"] = related_notes
    
    except Exception as e:
        print(f"Neo4j related notes error: {e}")
    
    # ============================================
    # STEP 4: Query Neo4j for learning path
    # ============================================
    # Find the prerequisite chain for matched topics
    # This shows: "Learn A → then B → then C"
    try:
        if topic_ids:
            # Get the prerequisite chain leading to the first matched topic
            learning_path = run_query(
                """
                MATCH (t:Topic)
                WHERE t.topicId IN $topicIds
                OPTIONAL MATCH path = (prereq:Topic)-[:PREREQUISITE_OF*1..5]->(t)
                WITH t, nodes(path) AS pathNodes
                UNWIND CASE WHEN pathNodes IS NULL THEN [t] ELSE pathNodes END AS node
                RETURN DISTINCT node.name AS name, node.topicId AS id
                """,
                {"topicIds": topic_ids}
            )
            # Extract unique names preserving order
            seen = set()
            path_names = []
            for item in learning_path:
                if item["name"] and item["name"] not in seen:
                    seen.add(item["name"])
                    path_names.append(item["name"])
            result["learningPath"] = path_names
    
    except Exception as e:
        print(f"Neo4j learning path error: {e}")
    
    return result


def search_notes_by_subject(subject_id: str) -> List[dict]:
    """Search notes filtered by subject (MongoDB query)."""
    db = get_db()
    notes = list(db["notes"].find({"subjectId": subject_id}).limit(50))
    for note in notes:
        note["_id"] = str(note["_id"])
        student = db["students"].find_one({"_id": note.get("uploadedBy")})
        note["uploaderName"] = student["name"] if student else "Unknown"
    return notes


def search_notes_by_topic(topic_id: str) -> List[dict]:
    """Search notes filtered by topic (MongoDB query)."""
    db = get_db()
    notes = list(db["notes"].find({"topicId": topic_id}).limit(50))
    for note in notes:
        note["_id"] = str(note["_id"])
        student = db["students"].find_one({"_id": note.get("uploadedBy")})
        note["uploaderName"] = student["name"] if student else "Unknown"
    return notes
