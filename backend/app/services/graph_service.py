"""
graph_service.py - Neo4j Graph Query Service
==============================================
This file contains all the graph-specific queries using Cypher.

These queries demonstrate WHY we need a graph database:
- Finding related content through multiple hops
- Discovering learning paths (prerequisites)
- Social features (who follows whom, recommendations)
- These would require complex, slow JOINs in SQL or MongoDB
- In Neo4j, they're natural and fast!

Each function includes:
- The Cypher query
- Explanation of what it does
- How the frontend uses the result
"""

from typing import List, Dict
from app.database.neo4j_db import run_query


# ============================================
# USE CASE A: Find all notes about a topic
# ============================================
def get_notes_for_topic(topic_id: str) -> List[dict]:
    """
    Find all notes about a specific topic using Neo4j.
    
    Cypher Pattern: (Note)-[:ABOUT]->(Topic)
    
    Frontend use: When a student clicks on a topic, show all related notes.
    
    Why Neo4j? We could do this in MongoDB too (filter by topicId),
    but Neo4j also gives us the UPLOADED student in the same query.
    """
    return run_query(
        """
        MATCH (n:Note)-[:ABOUT]->(t:Topic {topicId: $topicId})
        OPTIONAL MATCH (s:Student)-[:UPLOADED]->(n)
        RETURN n.noteId AS id, n.title AS title, 
               s.name AS uploader, t.name AS topic
        """,
        {"topicId": topic_id}
    )


# ============================================
# USE CASE B: Notes by followed students
# ============================================
def get_notes_by_followed(student_id: str) -> List[dict]:
    """
    Find notes uploaded by students whom the current user follows.
    
    Cypher Pattern: (me)-[:FOLLOWS]->(friend)-[:UPLOADED]->(Note)
    
    Frontend use: "Notes from people you follow" feed.
    
    Why Neo4j? This is a 2-hop traversal. In MongoDB, you'd need:
    1. Query follows collection to get followed student IDs
    2. Query notes collection filtered by those IDs
    Neo4j does it in ONE query!
    """
    return run_query(
        """
        MATCH (me:Student {studentId: $studentId})-[:FOLLOWS]->(friend:Student)-[:UPLOADED]->(n:Note)
        OPTIONAL MATCH (n)-[:ABOUT]->(t:Topic)
        RETURN n.noteId AS id, n.title AS title, 
               friend.name AS uploader, friend.studentId AS uploaderId,
               t.name AS topic
        ORDER BY n.title
        """,
        {"studentId": student_id}
    )


# ============================================
# USE CASE C: Related notes
# ============================================
def get_related_notes(note_id: str) -> List[dict]:
    """
    Find notes related to the currently opened note.
    
    Cypher Pattern: (Note)-[:RELATED_TO]-(OtherNote)
    Also finds notes about the same topic!
    
    Frontend use: "Related Notes" sidebar when viewing a note.
    
    Why Neo4j? The RELATED_TO relationship is explicitly modeled.
    In MongoDB, you'd need a separate "related" array and manage it manually.
    """
    return run_query(
        """
        MATCH (n:Note {noteId: $noteId})
        
        // Find directly related notes
        OPTIONAL MATCH (n)-[:RELATED_TO]-(related:Note)
        
        // Also find notes about the same topic
        OPTIONAL MATCH (n)-[:ABOUT]->(t:Topic)<-[:ABOUT]-(sameTopic:Note)
        WHERE sameTopic.noteId <> $noteId
        
        WITH COLLECT(DISTINCT {id: related.noteId, title: related.title, source: 'direct'}) + 
             COLLECT(DISTINCT {id: sameTopic.noteId, title: sameTopic.title, source: 'same_topic'}) AS allRelated
        UNWIND allRelated AS r
        WITH DISTINCT r.id AS id, r.title AS title, r.source AS source
        WHERE id IS NOT NULL
        RETURN id, title, source
        LIMIT 10
        """,
        {"noteId": note_id}
    )


# ============================================
# USE CASE D: Prerequisite topics
# ============================================
def get_prerequisites(topic_id: str) -> List[dict]:
    """
    Find prerequisite topics needed before learning a particular topic.
    
    Cypher Pattern: (Prereq)-[:PREREQUISITE_OF*]->(TargetTopic)
    The * means follow the chain multiple hops (up to 5).
    
    Frontend use: "Before studying X, you should learn:" panel.
    
    Why Neo4j? This is recursive graph traversal - exactly what
    graph databases are designed for. In SQL, you'd need recursive CTEs.
    In MongoDB, it's extremely difficult.
    """
    return run_query(
        """
        MATCH path = (prereq:Topic)-[:PREREQUISITE_OF*1..5]->(target:Topic {topicId: $topicId})
        WITH nodes(path) AS pathNodes
        UNWIND pathNodes AS node
        WITH DISTINCT node
        RETURN node.topicId AS id, node.name AS name
        ORDER BY node.name
        """,
        {"topicId": topic_id}
    )


# ============================================
# USE CASE E: Recommend notes for a student
# ============================================
def recommend_notes(student_id: str) -> List[dict]:
    """
    Recommend notes based on topics the student studies or has bookmarked.
    
    Logic:
    1. Find topics the student STUDIES
    2. Find topics of notes the student BOOKMARKED
    3. Find OTHER notes about those topics (or related topics)
    4. Exclude notes the student already uploaded or liked
    
    Frontend use: "Recommended for You" section on dashboard.
    
    Why Neo4j? This recommendation query traverses multiple relationships
    (STUDIES, BOOKMARKED, ABOUT, PREREQUISITE_OF) - a natural graph problem!
    """
    return run_query(
        """
        MATCH (me:Student {studentId: $studentId})
        
        // Find topics I study or have bookmarked notes about
        OPTIONAL MATCH (me)-[:STUDIES]->(studyTopic:Topic)
        OPTIONAL MATCH (me)-[:BOOKMARKED]->(bNote:Note)-[:ABOUT]->(bTopic:Topic)
        
        WITH me, COLLECT(DISTINCT studyTopic) + COLLECT(DISTINCT bTopic) AS myTopics
        UNWIND myTopics AS topic
        
        // Find notes about those topics (or related topics)
        MATCH (rec:Note)-[:ABOUT]->(topic)
        
        // Exclude notes I already uploaded or liked
        WHERE NOT (me)-[:UPLOADED]->(rec)
          AND NOT (me)-[:LIKED]->(rec)
        
        OPTIONAL MATCH (uploader:Student)-[:UPLOADED]->(rec)
        
        RETURN DISTINCT rec.noteId AS id, rec.title AS title, 
               uploader.name AS uploader, topic.name AS topic
        LIMIT 10
        """,
        {"studentId": student_id}
    )


# ============================================
# USE CASE F: Shortest path between topics
# ============================================
def shortest_path_between_topics(topic_id_1: str, topic_id_2: str) -> dict:
    """
    Find the shortest relationship path between two topics.
    
    Uses Neo4j's built-in shortestPath() function.
    Limited to 10 hops to prevent expensive queries.
    
    Frontend use: "How are these topics connected?" visualization.
    
    Why Neo4j? shortestPath is a built-in graph algorithm.
    Implementing this in SQL or MongoDB would be extremely complex.
    """
    results = run_query(
        """
        MATCH (t1:Topic {topicId: $id1}), (t2:Topic {topicId: $id2})
        MATCH path = shortestPath((t1)-[*..10]-(t2))
        RETURN [node IN nodes(path) | 
            CASE 
                WHEN node:Topic THEN {type: 'Topic', id: node.topicId, name: node.name}
                WHEN node:Subject THEN {type: 'Subject', id: node.subjectId, name: node.name}
                WHEN node:Note THEN {type: 'Note', id: node.noteId, name: node.title}
                WHEN node:Student THEN {type: 'Student', id: node.studentId, name: node.name}
                ELSE {type: 'Unknown', name: 'Unknown'}
            END
        ] AS path,
        [rel IN relationships(path) | type(rel)] AS relationshipTypes,
        length(path) AS pathLength
        """,
        {"id1": topic_id_1, "id2": topic_id_2}
    )
    
    if results:
        return results[0]
    return {"path": [], "relationshipTypes": [], "pathLength": -1}


# ============================================
# ADDITIONAL: Get student's learning connections
# ============================================
def get_student_connections(student_id: str) -> dict:
    """
    Get a student's full learning network:
    - Topics they study
    - Notes they uploaded, liked, bookmarked
    - Students they follow
    - Students who follow them
    
    Frontend use: Student profile / dashboard page.
    """
    # Topics the student studies
    topics = run_query(
        """
        MATCH (s:Student {studentId: $sid})-[:STUDIES]->(t:Topic)
        OPTIONAL MATCH (t)-[:PART_OF]->(sub:Subject)
        RETURN t.topicId AS id, t.name AS name, sub.name AS subject
        """,
        {"sid": student_id}
    )
    
    # Notes uploaded
    uploaded = run_query(
        """
        MATCH (s:Student {studentId: $sid})-[:UPLOADED]->(n:Note)
        OPTIONAL MATCH (n)-[:ABOUT]->(t:Topic)
        RETURN n.noteId AS id, n.title AS title, t.name AS topic
        """,
        {"sid": student_id}
    )
    
    # Students followed
    following = run_query(
        """
        MATCH (s:Student {studentId: $sid})-[:FOLLOWS]->(f:Student)
        RETURN f.studentId AS id, f.name AS name
        """,
        {"sid": student_id}
    )
    
    # Students who follow this student
    followers = run_query(
        """
        MATCH (f:Student)-[:FOLLOWS]->(s:Student {studentId: $sid})
        RETURN f.studentId AS id, f.name AS name
        """,
        {"sid": student_id}
    )
    
    return {
        "topics": topics,
        "uploaded": uploaded,
        "following": following,
        "followers": followers
    }


# ============================================
# Dashboard stats
# ============================================
def get_dashboard_stats() -> dict:
    """
    Get overview statistics from Neo4j for the dashboard.
    """
    stats = run_query(
        """
        MATCH (s:Student) WITH count(s) AS students
        MATCH (n:Note) WITH students, count(n) AS notes
        MATCH (t:Topic) WITH students, notes, count(t) AS topics
        MATCH (sub:Subject) WITH students, notes, topics, count(sub) AS subjects
        RETURN students, notes, topics, subjects
        """
    )
    
    if stats:
        return stats[0]
    return {"students": 0, "notes": 0, "topics": 0, "subjects": 0}


def get_subject_topic_tree() -> List[dict]:
    """
    Get all subjects with their topics and note counts.
    Used for the sidebar/navigation tree.
    """
    return run_query(
        """
        MATCH (sub:Subject)<-[:PART_OF]-(t:Topic)
        OPTIONAL MATCH (n:Note)-[:ABOUT]->(t)
        RETURN sub.subjectId AS subjectId, sub.name AS subjectName,
               t.topicId AS topicId, t.name AS topicName,
               count(n) AS noteCount
        ORDER BY sub.name, t.name
        """
    )
