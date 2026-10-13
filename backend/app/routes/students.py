"""
students.py - Student API Routes
==================================
Handles student registration, login, and profile management.

Authentication flow:
1. Student registers with name, email, password
2. Password is hashed with bcrypt (never stored as plain text!)
3. On login, password is verified against the hash
4. If correct, a JWT token is returned
5. Frontend sends this token with every subsequent request
6. Backend verifies the token to identify the student
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
from typing import Optional

from app.database.mongodb import get_db
from app.database.neo4j_db import run_query
from app.config import settings
from app.models.schemas import (
    StudentCreate, StudentLogin, StudentResponse, 
    TokenResponse, MessageResponse
)

router = APIRouter()


# ========================
# HELPER FUNCTIONS
# ========================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_token(student_id: str) -> str:
    """Create a JWT token for a student."""
    payload = {
        "sub": student_id,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_student(authorization: Optional[str] = Header(None)) -> dict:
    """
    Extract the student ID from the JWT token in the Authorization header.
    
    The frontend sends: Authorization: Bearer <token>
    We decode the token to get the student ID.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        student_id = payload.get("sub")
        if not student_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = get_db()
        student = db["students"].find_one({"_id": student_id})
        if not student:
            raise HTTPException(status_code=401, detail="Student not found")
        
        return student
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def _generate_student_id(db) -> str:
    """Generate the next student ID (S101, S102, etc.)."""
    # Find the highest existing student ID
    last = db["students"].find_one(sort=[("_id", -1)])
    if last:
        # Extract number from ID like "S105" -> 105
        try:
            num = int(last["_id"][1:]) + 1
        except (ValueError, IndexError):
            num = 200  # Start from S200 for new registrations
    else:
        num = 101
    return f"S{num}"


# ========================
# API ROUTES
# ========================

@router.post("/students/register", response_model=TokenResponse)
def register(student: StudentCreate):
    """
    Register a new student.
    
    Steps:
    1. Check if email already exists
    2. Generate a new student ID
    3. Hash the password
    4. Save to MongoDB
    5. Create a Student node in Neo4j
    6. Return a JWT token
    """
    db = get_db()
    
    # Check if email already exists
    existing = db["students"].find_one({"email": student.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate student ID and create document
    student_id = _generate_student_id(db)
    student_doc = {
        "_id": student_id,
        "name": student.name,
        "email": student.email,
        "password_hash": hash_password(student.password),
        "department": student.department,
        "semester": student.semester,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Save to MongoDB
    db["students"].insert_one(student_doc)
    
    # Create node in Neo4j
    try:
        run_query(
            "MERGE (s:Student {studentId: $id}) SET s.name = $name",
            {"id": student_id, "name": student.name}
        )
    except Exception as e:
        print(f"Warning: Failed to create Neo4j node for student {student_id}: {e}")
    
    # Return token
    token = create_token(student_id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "student": {
            "_id": student_id,
            "name": student.name,
            "email": student.email,
            "department": student.department,
            "semester": student.semester
        }
    }


@router.post("/students/login", response_model=TokenResponse)
def login(credentials: StudentLogin):
    """
    Log in a student.
    
    Steps:
    1. Find student by email in MongoDB
    2. Verify password against stored hash
    3. Return JWT token if correct
    """
    db = get_db()
    
    student = db["students"].find_one({"email": credentials.email})
    if not student:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(credentials.password, student["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(student["_id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "student": {
            "_id": student["_id"],
            "name": student["name"],
            "email": student["email"],
            "department": student["department"],
            "semester": student["semester"]
        }
    }


@router.get("/students/me")
def get_profile(student: dict = Depends(get_current_student)):
    """Get the current logged-in student's profile."""
    return {
        "_id": student["_id"],
        "name": student["name"],
        "email": student["email"],
        "department": student["department"],
        "semester": student["semester"],
        "created_at": student.get("created_at")
    }


@router.get("/students/{student_id}")
def get_student(student_id: str):
    """Get a student's public profile."""
    db = get_db()
    student = db["students"].find_one({"_id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "_id": student["_id"],
        "name": student["name"],
        "department": student["department"],
        "semester": student["semester"]
    }


@router.get("/students")
def list_students():
    """List all students (for demo purposes)."""
    db = get_db()
    students = list(db["students"].find(
        {},
        {"password_hash": 0}  # Exclude password hash!
    ))
    for s in students:
        s["_id"] = str(s["_id"])
    return students


@router.post("/students/{student_id}/follow/{target_id}")
def follow_student(student_id: str, target_id: str):
    """Follow another student."""
    if student_id == target_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    try:
        run_query(
            "MATCH (s1:Student {studentId: $from}), (s2:Student {studentId: $to}) "
            "MERGE (s1)-[:FOLLOWS]->(s2)",
            {"from": student_id, "to": target_id}
        )
        return {"message": f"Student {student_id} now follows {target_id}", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
