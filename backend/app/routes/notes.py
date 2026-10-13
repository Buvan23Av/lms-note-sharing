"""
notes.py - Notes API Routes
=============================
Handles CRUD operations for notes, plus likes, bookmarks, and comments.

Note storage strategy:
- MongoDB stores: full note details, file metadata, comments, bookmarks
- Neo4j stores: note relationships (ABOUT topic, UPLOADED by student, RELATED_TO other notes)
- Both share the same note IDs (e.g., 'N101')

When to EMBED vs REFERENCE in MongoDB:
- EMBED: data that's always read together (tags in notes, they're always shown)
- REFERENCE: data that grows unbounded or is shared (comments reference notes by ID)
"""

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from datetime import datetime
from typing import Optional, List

from app.database.mongodb import get_db
from app.database.neo4j_db import run_query
from app.config import settings
from app.models.schemas import NoteCreate, CommentCreate

router = APIRouter()


def _generate_note_id(db) -> str:
    """Generate the next note ID."""
    last = db["notes"].find_one(sort=[("_id", -1)])
    if last:
        try:
            num = int(last["_id"][1:]) + 1
        except (ValueError, IndexError):
            num = 200
    else:
        num = 101
    return f"N{num}"


def _generate_comment_id(db) -> str:
    """Generate the next comment ID."""
    last = db["comments"].find_one(sort=[("_id", -1)])
    if last:
        try:
            num = int(last["_id"][1:]) + 1
        except (ValueError, IndexError):
            num = 100
    else:
        num = 1
    return f"C{num}"


# ========================
# NOTE CRUD
# ========================

@router.get("/notes")
def list_notes(
    subject: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = Query(default=50, le=100)
):
    """
    List notes with optional filters.
    Demonstrates MongoDB query filtering.
    """
    db = get_db()
    
    # Build filter query
    query_filter = {}
    if subject:
        query_filter["subjectId"] = subject
    if topic:
        query_filter["topicId"] = topic
    
    notes = list(db["notes"].find(query_filter).sort("created_at", -1).limit(limit))
    
    # Enrich with related names
    for note in notes:
        note["_id"] = str(note["_id"])
        student = db["students"].find_one({"_id": note.get("uploadedBy")})
        note["uploaderName"] = student["name"] if student else "Unknown"
        subject_doc = db["subjects"].find_one({"_id": note.get("subjectId")})
        note["subjectName"] = subject_doc["name"] if subject_doc else "Unknown"
        topic_doc = db["topics"].find_one({"_id": note.get("topicId")})
        note["topicName"] = topic_doc["name"] if topic_doc else "Unknown"
    
    return notes


@router.get("/notes/{note_id}")
def get_note(note_id: str):
    """Get a single note with full details."""
    db = get_db()
    note = db["notes"].find_one({"_id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note["_id"] = str(note["_id"])
    student = db["students"].find_one({"_id": note.get("uploadedBy")})
    note["uploaderName"] = student["name"] if student else "Unknown"
    subject_doc = db["subjects"].find_one({"_id": note.get("subjectId")})
    note["subjectName"] = subject_doc["name"] if subject_doc else "Unknown"
    topic_doc = db["topics"].find_one({"_id": note.get("topicId")})
    note["topicName"] = topic_doc["name"] if topic_doc else "Unknown"
    
    # Get comments from MongoDB
    comments = list(db["comments"].find({"noteId": note_id}).sort("created_at", -1))
    for comment in comments:
        comment["_id"] = str(comment["_id"])
        commenter = db["students"].find_one({"_id": comment.get("studentId")})
        comment["studentName"] = commenter["name"] if commenter else "Unknown"
    note["comments"] = comments
    
    # Get related notes from Neo4j
    try:
        from app.services.graph_service import get_related_notes
        note["relatedNotes"] = get_related_notes(note_id)
    except Exception:
        note["relatedNotes"] = []
    
    return note


@router.post("/notes")
def create_note(
    title: str = Form(...),
    description: str = Form(...),
    subjectId: str = Form(...),
    topicId: str = Form(...),
    tags: str = Form(default=""),
    uploadedBy: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Create a new note with optional file upload.
    
    Saves to BOTH MongoDB (details) and Neo4j (relationships).
    """
    db = get_db()
    note_id = _generate_note_id(db)
    
    # Handle file upload
    file_url = ""
    if file:
        # Validate file type
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Save file
        file_path = os.path.join(settings.UPLOAD_DIR, f"{note_id}{ext}")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            content = file.file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large (max 10MB)")
            f.write(content)
        file_url = f"/uploads/{note_id}{ext}"
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    # Create MongoDB document
    note_doc = {
        "_id": note_id,
        "title": title,
        "description": description,
        "uploadedBy": uploadedBy,
        "subjectId": subjectId,
        "topicId": topicId,
        "tags": tag_list,
        "fileUrl": file_url,
        "likes": 0,
        "created_at": datetime.utcnow().isoformat()
    }
    db["notes"].insert_one(note_doc)
    
    # Create Neo4j node and relationships
    try:
        run_query(
            "MERGE (n:Note {noteId: $nid}) SET n.title = $title",
            {"nid": note_id, "title": title}
        )
        run_query(
            "MATCH (s:Student {studentId: $sid}), (n:Note {noteId: $nid}) "
            "MERGE (s)-[:UPLOADED]->(n)",
            {"sid": uploadedBy, "nid": note_id}
        )
        run_query(
            "MATCH (n:Note {noteId: $nid}), (t:Topic {topicId: $tid}) "
            "MERGE (n)-[:ABOUT]->(t)",
            {"nid": note_id, "tid": topicId}
        )
    except Exception as e:
        print(f"Warning: Neo4j update failed for note {note_id}: {e}")
    
    note_doc["_id"] = str(note_doc["_id"])
    return {"message": "Note created successfully", "note": note_doc}


# ========================
# LIKES
# ========================

@router.post("/notes/{note_id}/like")
def like_note(note_id: str, student_id: str = Query(...)):
    """
    Like a note. Updates both MongoDB (like count) and Neo4j (LIKED relationship).
    """
    db = get_db()
    
    note = db["notes"].find_one({"_id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Increment like count in MongoDB
    db["notes"].update_one({"_id": note_id}, {"$inc": {"likes": 1}})
    
    # Create LIKED relationship in Neo4j
    try:
        run_query(
            "MATCH (s:Student {studentId: $sid}), (n:Note {noteId: $nid}) "
            "MERGE (s)-[:LIKED]->(n)",
            {"sid": student_id, "nid": note_id}
        )
    except Exception as e:
        print(f"Warning: Neo4j LIKED failed: {e}")
    
    return {"message": "Note liked!", "success": True}


# ========================
# BOOKMARKS
# ========================

@router.post("/notes/{note_id}/bookmark")
def bookmark_note(note_id: str, student_id: str = Query(...)):
    """
    Bookmark a note. Saves to MongoDB bookmarks collection AND Neo4j.
    """
    db = get_db()
    
    note = db["notes"].find_one({"_id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Save bookmark in MongoDB (upsert to prevent duplicates)
    bookmark_id = f"{student_id}_{note_id}"
    db["bookmarks"].update_one(
        {"_id": bookmark_id},
        {"$set": {
            "studentId": student_id,
            "noteId": note_id,
            "created_at": datetime.utcnow().isoformat()
        }},
        upsert=True
    )
    
    # Create BOOKMARKED relationship in Neo4j
    try:
        run_query(
            "MATCH (s:Student {studentId: $sid}), (n:Note {noteId: $nid}) "
            "MERGE (s)-[:BOOKMARKED]->(n)",
            {"sid": student_id, "nid": note_id}
        )
    except Exception as e:
        print(f"Warning: Neo4j BOOKMARKED failed: {e}")
    
    return {"message": "Note bookmarked!", "success": True}


@router.get("/students/{student_id}/bookmarks")
def get_bookmarks(student_id: str):
    """Get all bookmarked notes for a student."""
    db = get_db()
    bookmarks = list(db["bookmarks"].find({"studentId": student_id}))
    
    notes = []
    for bm in bookmarks:
        note = db["notes"].find_one({"_id": bm["noteId"]})
        if note:
            note["_id"] = str(note["_id"])
            notes.append(note)
    
    return notes


# ========================
# COMMENTS
# ========================

@router.post("/notes/{note_id}/comments")
def add_comment(note_id: str, student_id: str = Query(...), text: str = Query(...)):
    """
    Add a comment to a note.
    Comments are stored in MongoDB (document storage is ideal for this).
    """
    db = get_db()
    
    note = db["notes"].find_one({"_id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    comment_id = _generate_comment_id(db)
    comment = {
        "_id": comment_id,
        "noteId": note_id,
        "studentId": student_id,
        "text": text,
        "created_at": datetime.utcnow().isoformat()
    }
    db["comments"].insert_one(comment)
    
    # Get commenter name
    student = db["students"].find_one({"_id": student_id})
    comment["studentName"] = student["name"] if student else "Unknown"
    comment["_id"] = str(comment["_id"])
    
    return {"message": "Comment added!", "comment": comment}


@router.get("/notes/{note_id}/comments")
def get_comments(note_id: str):
    """Get all comments for a note."""
    db = get_db()
    comments = list(db["comments"].find({"noteId": note_id}).sort("created_at", -1))
    
    for comment in comments:
        comment["_id"] = str(comment["_id"])
        student = db["students"].find_one({"_id": comment.get("studentId")})
        comment["studentName"] = student["name"] if student else "Unknown"
    
    return comments


# ========================
# SUBJECTS & TOPICS
# ========================

@router.get("/subjects")
def list_subjects():
    """List all subjects."""
    db = get_db()
    subjects = list(db["subjects"].find())
    for s in subjects:
        s["_id"] = str(s["_id"])
    return subjects


@router.get("/topics")
def list_topics(subject_id: Optional[str] = None):
    """List topics, optionally filtered by subject."""
    db = get_db()
    query = {"subjectId": subject_id} if subject_id else {}
    topics = list(db["topics"].find(query))
    for t in topics:
        t["_id"] = str(t["_id"])
    return topics
