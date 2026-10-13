"""
integration.py - Data Integration API Routes
==============================================
Handles XML data import and export.

These endpoints let you:
1. Import data from the XML file into both databases
2. Export current data as XML
3. Check the status of both databases
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response

from app.services.xml_importer import run_import, XMLImporter
from app.models.schemas import ImportResult
from app.database.mongodb import get_db
from app.database.neo4j_db import run_query

router = APIRouter()


@router.post("/import/xml", response_model=ImportResult)
def import_xml_data():
    """
    Import data from the default lms_data.xml file.
    
    This endpoint:
    1. Reads backend/data/lms_data.xml
    2. Parses XML into Python objects
    3. Writes to MongoDB (with upsert to prevent duplicates)
    4. Creates Neo4j nodes and relationships (with MERGE)
    5. Returns counts and any errors
    
    Safe to call multiple times - uses upsert/MERGE!
    """
    try:
        result = run_import()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/xml/upload")
def import_uploaded_xml(file: UploadFile = File(...)):
    """
    Import data from an uploaded XML file.
    """
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="Only XML files are allowed")
    
    # Save uploaded file temporarily
    temp_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "uploaded_import.xml"
    )
    
    try:
        with open(temp_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        importer = XMLImporter(temp_path)
        result = importer.import_all()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/export/xml")
def export_as_xml():
    """
    Export current MongoDB data as XML.
    Demonstrates the reverse of import.
    """
    db = get_db()
    
    # Build XML tree
    root = ET.Element("lms")
    
    # Export students
    students_elem = ET.SubElement(root, "students")
    for student in db["students"].find({}, {"password_hash": 0}):
        s_elem = ET.SubElement(students_elem, "student", id=str(student["_id"]))
        ET.SubElement(s_elem, "name").text = student.get("name", "")
        ET.SubElement(s_elem, "email").text = student.get("email", "")
        ET.SubElement(s_elem, "department").text = student.get("department", "")
        ET.SubElement(s_elem, "semester").text = str(student.get("semester", ""))
    
    # Export subjects
    subjects_elem = ET.SubElement(root, "subjects")
    for subject in db["subjects"].find():
        s_elem = ET.SubElement(subjects_elem, "subject", id=str(subject["_id"]))
        ET.SubElement(s_elem, "name").text = subject.get("name", "")
        ET.SubElement(s_elem, "code").text = subject.get("code", "")
        ET.SubElement(s_elem, "department").text = subject.get("department", "")
        ET.SubElement(s_elem, "semester").text = str(subject.get("semester", ""))
    
    # Export topics
    topics_elem = ET.SubElement(root, "topics")
    for topic in db["topics"].find():
        t_elem = ET.SubElement(topics_elem, "topic", id=str(topic["_id"]), subjectId=topic.get("subjectId", ""))
        ET.SubElement(t_elem, "name").text = topic.get("name", "")
        ET.SubElement(t_elem, "description").text = topic.get("description", "")
    
    # Export notes
    notes_elem = ET.SubElement(root, "notes")
    for note in db["notes"].find():
        n_elem = ET.SubElement(notes_elem, "note", 
            id=str(note["_id"]), 
            uploaderId=note.get("uploadedBy", ""),
            topicId=note.get("topicId", ""),
            subjectId=note.get("subjectId", "")
        )
        ET.SubElement(n_elem, "title").text = note.get("title", "")
        ET.SubElement(n_elem, "description").text = note.get("description", "")
        ET.SubElement(n_elem, "tags").text = ",".join(note.get("tags", []))
    
    # Convert to string with pretty printing
    xml_string = minidom.parseString(
        ET.tostring(root, encoding='unicode')
    ).toprettyxml(indent="  ")
    
    return Response(
        content=xml_string,
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=lms_export.xml"}
    )


@router.get("/status")
def integration_status():
    """
    Check the status of both databases and data counts.
    Useful for verifying that import worked correctly.
    """
    result = {
        "mongodb": {"status": "disconnected", "counts": {}},
        "neo4j": {"status": "disconnected", "counts": {}}
    }
    
    # Check MongoDB
    try:
        db = get_db()
        db.command('ping')
        result["mongodb"]["status"] = "connected"
        for coll in ["students", "subjects", "topics", "notes", "comments", "bookmarks"]:
            result["mongodb"]["counts"][coll] = db[coll].count_documents({})
    except Exception as e:
        result["mongodb"]["error"] = str(e)
    
    # Check Neo4j
    try:
        stats = run_query(
            "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label"
        )
        result["neo4j"]["status"] = "connected"
        for stat in stats:
            result["neo4j"]["counts"][stat["label"]] = stat["count"]
        
        # Count relationships
        rel_stats = run_query(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY type"
        )
        result["neo4j"]["relationships"] = {r["type"]: r["count"] for r in rel_stats}
    except Exception as e:
        result["neo4j"]["error"] = str(e)
    
    return result
