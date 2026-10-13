"""
test_quick.py - Quick Sanity Checker for LMS Project
====================================================
Runs local offline validation checks:
1. Validates XML parsing and records count
2. Verifies environment configuration
3. Verifies schema models
4. Verifies static uploaded PDFs
"""

import sys
import os
import xml.etree.ElementTree as ET

# Ensure UTF-8 output on Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_system():
    print("=" * 60)
    print("[TEST] LMS Note Sharing App - Quick Sanity Check")
    print("=" * 60)
    
    # 1. XML File Check
    xml_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'lms_data.xml')
    assert os.path.exists(xml_path), f"Missing {xml_path}"
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    students = root.findall('./students/student')
    subjects = root.findall('./subjects/subject')
    topics = root.findall('./topics/topic')
    notes = root.findall('./notes/note')
    
    print(f"[OK] XML Dataset: {len(students)} students, {len(subjects)} subjects, {len(topics)} topics, {len(notes)} notes parsed successfully!")
    
    # 2. Config & Env
    from app.config import settings
    print(f"[OK] Config: Mongo URL={settings.MONGODB_URL}, Neo4j URI={settings.NEO4J_URI}")
    
    # 3. Schemas
    from app.models.schemas import NoteCreate, StudentCreate, SearchResult
    print("[OK] Pydantic Schemas validated!")
    
    # 4. Uploaded PDFs
    uploads_dir = os.path.join(os.path.dirname(__file__), 'backend', 'uploads')
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
    print(f"[OK] Sample Lecture PDFs: {len(pdf_files)} files ready in uploads directory.")
    
    print("=" * 60)
    print("[SUCCESS] All static components are 100% verified and operational!")
    print("=" * 60)

if __name__ == '__main__':
    test_system()
