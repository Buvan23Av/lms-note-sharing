"""
schemas.py - Pydantic Data Models (Schemas)
=============================================
Pydantic models define the SHAPE of data flowing through the API.

Why Pydantic?
- Automatic validation: rejects bad data before it reaches the database
- Auto-generates Swagger docs: you can see expected fields in /docs
- Type hints: your IDE shows you what fields are available

Naming convention:
- XxxCreate: data sent BY the user to CREATE something
- XxxResponse: data sent TO the user as a response
- XxxUpdate: data sent BY the user to UPDATE something
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# ========================
# STUDENT SCHEMAS
# ========================

class StudentCreate(BaseModel):
    """Data required to register a new student."""
    name: str = Field(..., min_length=2, max_length=100, description="Student's full name")
    email: str = Field(..., description="Student's email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    department: str = Field(..., description="Department like CSE, ECE, MECH")
    semester: int = Field(..., ge=1, le=8, description="Current semester (1-8)")


class StudentLogin(BaseModel):
    """Data required to log in."""
    email: str
    password: str


class StudentResponse(BaseModel):
    """Student data returned to the frontend (never includes password!)."""
    id: str = Field(..., alias="_id")
    name: str
    email: str
    department: str
    semester: int
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# ========================
# NOTE SCHEMAS  
# ========================

class NoteCreate(BaseModel):
    """Data required to upload a new note."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    subjectId: str = Field(..., description="ID of the subject (e.g., SUB101)")
    topicId: str = Field(..., description="ID of the topic (e.g., T101)")
    tags: List[str] = Field(default=[], description="Tags for searching")


class NoteResponse(BaseModel):
    """Note data returned to the frontend."""
    id: str = Field(..., alias="_id")
    title: str
    description: str
    uploadedBy: str
    uploaderName: Optional[str] = None
    subjectId: str
    subjectName: Optional[str] = None
    topicId: str
    topicName: Optional[str] = None
    tags: List[str] = []
    fileUrl: Optional[str] = None
    likes: int = 0
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# ========================
# COMMENT SCHEMAS
# ========================

class CommentCreate(BaseModel):
    """Data required to add a comment."""
    text: str = Field(..., min_length=1, max_length=500)


class CommentResponse(BaseModel):
    """Comment data returned to the frontend."""
    id: str = Field(..., alias="_id")
    noteId: str
    studentId: str
    studentName: Optional[str] = None
    text: str
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True


# ========================
# SEARCH SCHEMAS
# ========================

class SearchResult(BaseModel):
    """
    Combined search result from MongoDB + Neo4j.
    This is the KEY schema for the multi-database query requirement!
    """
    query: str
    notes: List[dict] = Field(default=[], description="Notes from MongoDB text search")
    relatedTopics: List[dict] = Field(default=[], description="Related topics from Neo4j")
    relatedNotes: List[dict] = Field(default=[], description="Related notes from Neo4j graph")
    learningPath: List[str] = Field(default=[], description="Prerequisite chain from Neo4j")


# ========================
# SUBJECT & TOPIC SCHEMAS
# ========================

class SubjectResponse(BaseModel):
    """Subject data for dropdowns and filters."""
    id: str = Field(..., alias="_id")
    name: str
    code: str
    department: str
    semester: int

    class Config:
        populate_by_name = True


class TopicResponse(BaseModel):
    """Topic data."""
    id: str = Field(..., alias="_id")
    name: str
    subjectId: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True


# ========================
# XML IMPORT SCHEMAS
# ========================

class ImportResult(BaseModel):
    """Result of XML data import operation."""
    success: bool
    message: str
    mongodb_counts: dict = Field(default={}, description="Records imported to MongoDB")
    neo4j_counts: dict = Field(default={}, description="Nodes/relationships created in Neo4j")
    errors: List[str] = Field(default=[], description="Any errors encountered")


# ========================
# GENERAL SCHEMAS
# ========================

class TokenResponse(BaseModel):
    """JWT token returned after login."""
    access_token: str
    token_type: str = "bearer"
    student: dict


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    success: bool = True
