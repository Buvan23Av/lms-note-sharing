"""
neo4j_db.py - Neo4j Graph Database Connection Manager
=====================================================
This file handles connecting to Neo4j using the official Python driver.

Why Neo4j?
- MongoDB is great for storing document details (notes, profiles, comments)
- But Neo4j excels at RELATIONSHIPS between data:
  - "Which notes are related to this topic?"
  - "What should I learn before this topic?" (prerequisites)
  - "What do students who liked this note also like?" (recommendations)

Neo4j stores data as:
- Nodes: entities like Student, Note, Topic, Subject
- Relationships: connections like UPLOADED, LIKED, PREREQUISITE_OF
- Properties: data on nodes/relationships like name, title, date

This is called a 'Property Graph' model.
"""

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from app.config import settings

# Module-level variable to hold our driver
_driver = None


def connect_neo4j():
    """
    Establish connection to Neo4j server.
    Called once when the FastAPI app starts up.
    
    Returns:
        The Neo4j driver if connection succeeds, None otherwise.
    """
    global _driver
    try:
        # Create the Neo4j driver
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        
        # Verify the connection works
        _driver.verify_connectivity()
        
        # Create constraints and indexes in Neo4j
        _create_constraints()
        
        print(f"[OK] Connected to Neo4j: {settings.NEO4J_URI}")
        return _driver
        
    except ServiceUnavailable as e:
        print(f"[ERROR] Failed to connect to Neo4j: {e}")
        print("        Make sure Neo4j is running (docker-compose up -d)")
        return None
    except AuthError as e:
        print(f"[ERROR] Neo4j authentication failed: {e}")
        print("        Check NEO4J_USER and NEO4J_PASSWORD in .env")
        return None


def get_driver():
    """
    Get the Neo4j driver for running queries.
    
    Usage:
        from app.database.neo4j_db import get_driver
        driver = get_driver()
        with driver.session() as session:
            result = session.run("MATCH (n:Student) RETURN n")
    """
    if _driver is None:
        raise Exception(
            "Neo4j is not connected! "
            "Make sure Neo4j is running and connect_neo4j() was called."
        )
    return _driver


def run_query(cypher, parameters=None):
    """
    Run a Cypher query and return the results as a list of dictionaries.
    
    This is a convenience function so you don't have to manage sessions
    manually every time.
    
    Args:
        cypher: The Cypher query string (Neo4j's query language)
        parameters: Dictionary of query parameters (prevents injection attacks!)
    
    Returns:
        List of dictionaries, where each dict is one result row.
    
    Example:
        results = run_query(
            "MATCH (s:Student {studentId: $sid}) RETURN s.name AS name",
            {"sid": "S101"}
        )
        # results = [{"name": "Arun"}]
    """
    driver = get_driver()
    with driver.session() as session:
        result = session.run(cypher, parameters or {})
        # Convert each record to a plain dictionary
        return [record.data() for record in result]


def _create_constraints():
    """
    Create uniqueness constraints in Neo4j.
    
    Constraints ensure:
    1. No two Student nodes have the same studentId
    2. No two Note nodes have the same noteId
    3. No two Topic nodes have the same topicId
    4. No two Subject nodes have the same subjectId
    
    These also automatically create indexes for fast lookups!
    
    MERGE queries rely on these constraints to prevent duplicates.
    """
    driver = get_driver()
    
    constraints = [
        ("student_id_unique", "CREATE CONSTRAINT student_id_unique IF NOT EXISTS FOR (s:Student) REQUIRE s.studentId IS UNIQUE"),
        ("note_id_unique", "CREATE CONSTRAINT note_id_unique IF NOT EXISTS FOR (n:Note) REQUIRE n.noteId IS UNIQUE"),
        ("topic_id_unique", "CREATE CONSTRAINT topic_id_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.topicId IS UNIQUE"),
        ("subject_id_unique", "CREATE CONSTRAINT subject_id_unique IF NOT EXISTS FOR (s:Subject) REQUIRE s.subjectId IS UNIQUE"),
    ]
    
    with driver.session() as session:
        for name, cypher in constraints:
            try:
                session.run(cypher)
            except Exception as e:
                # Constraint might already exist, that's fine
                print(f"   Note: Constraint '{name}' - {e}")
    
    print("   [CONSTRAINTS] Neo4j constraints created/verified")


def close_neo4j():
    """Close the Neo4j connection when the app shuts down."""
    global _driver
    if _driver:
        _driver.close()
        _driver = None
        print("Neo4j connection closed.")
