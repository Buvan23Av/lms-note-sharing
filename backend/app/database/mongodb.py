"""
mongodb.py - MongoDB Connection Manager
========================================
This file handles connecting to MongoDB using PyMongo.

Why PyMongo?
- It's the official MongoDB driver for Python
- Simple to use: connect, get database, get collection, run queries

Connection Flow:
1. App starts → connect_mongodb() is called
2. PyMongo connects to MongoDB server
3. We get a reference to our database (lms_db)
4. All other files import 'get_db()' to access collections

MongoDB stores data as 'documents' (like JSON objects) in 'collections' (like tables).
"""

from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings

# Module-level variables to hold our connection
_client: MongoClient = None
_db = None


def connect_mongodb():
    """
    Establish connection to MongoDB server.
    Called once when the FastAPI app starts up.
    
    Returns:
        The database object if connection succeeds, None otherwise.
    """
    global _client, _db
    try:
        # Create a MongoClient with a 5-second timeout
        # If MongoDB is not running, this will fail fast instead of hanging
        _client = MongoClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        
        # 'ping' the server to verify the connection actually works
        _client.admin.command('ping')
        
        # Get our database (creates it automatically if it doesn't exist)
        _db = _client[settings.MONGODB_DB_NAME]
        
        # Create indexes for faster searching
        _create_indexes()
        
        print(f"[OK] Connected to MongoDB: {settings.MONGODB_URL}")
        print(f"     Database: {settings.MONGODB_DB_NAME}")
        return _db
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"[ERROR] Failed to connect to MongoDB: {e}")
        print("        Make sure MongoDB is running (docker-compose up -d)")
        return None


def get_db():
    """
    Get the MongoDB database object.
    Other files import this to access collections.
    
    Usage:
        from app.database.mongodb import get_db
        db = get_db()
        notes = db["notes"].find({"tags": "DBMS"})
    """
    if _db is None:
        raise Exception(
            "MongoDB is not connected! "
            "Make sure MongoDB is running and connect_mongodb() was called."
        )
    return _db


def _create_indexes():
    """
    Create indexes on MongoDB collections for faster queries.
    
    Why indexes?
    - Without indexes, MongoDB scans EVERY document (slow!)
    - With indexes, MongoDB jumps directly to matching documents (fast!)
    
    Types of indexes used:
    - ASCENDING: For exact match queries (like finding by studentId)
    - TEXT: For full-text search (searching note titles and descriptions)
    """
    db = _db
    
    # --- Notes collection indexes ---
    # Text index: allows searching note titles, descriptions, and tags
    # You can only have ONE text index per collection
    db["notes"].create_index(
        [("title", TEXT), ("description", TEXT), ("tags", TEXT)],
        name="notes_text_search"
    )
    # Index for filtering notes by subject
    db["notes"].create_index([("subjectId", ASCENDING)], name="notes_by_subject")
    # Index for filtering notes by topic  
    db["notes"].create_index([("topicId", ASCENDING)], name="notes_by_topic")
    # Index for finding notes uploaded by a student
    db["notes"].create_index([("uploadedBy", ASCENDING)], name="notes_by_uploader")
    # Unique index on _id (ensures no duplicate note IDs)
    # MongoDB creates this automatically, but we ensure our custom IDs are unique
    
    # --- Students collection indexes ---
    db["students"].create_index([("email", ASCENDING)], unique=True, name="unique_email")
    
    # --- Comments collection indexes ---
    db["comments"].create_index([("noteId", ASCENDING)], name="comments_by_note")
    
    # --- Bookmarks collection indexes ---
    db["bookmarks"].create_index(
        [("studentId", ASCENDING), ("noteId", ASCENDING)],
        unique=True,
        name="unique_bookmark"
    )
    
    print("   [INDEXES] MongoDB indexes created/verified")


def close_mongodb():
    """Close the MongoDB connection when the app shuts down."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("MongoDB connection closed.")
