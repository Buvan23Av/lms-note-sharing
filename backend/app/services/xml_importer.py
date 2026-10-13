"""
xml_importer.py - XML Data Integration Service
================================================
This is the CORE of the multi-database integration requirement!

What this file does:
1. Reads the XML file (lms_data.xml) - the interchange format
2. Parses XML elements into Python dictionaries
3. Writes data to MongoDB (document database)
4. Creates corresponding nodes and relationships in Neo4j (graph database)
5. Prevents duplicates when importing the same XML multiple times
6. Reports success/error counts for each database separately

IMPORTANT CONCEPTS:
- XML is the DATA INTEGRATION FORMAT (bridges the two databases)
- MongoDB and Neo4j are SEPARATE databases (no shared transactions)
- We use the SAME IDs (like 'S101', 'N101') in both databases
- If one database fails, we still try to import into the other
- MERGE (Neo4j) and upsert (MongoDB) make imports idempotent

Data Flow:
  XML File → Parse → Python Dicts → MongoDB Documents
                                   → Neo4j Nodes/Relationships
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
import bcrypt
from typing import Dict, List, Tuple

from app.database.mongodb import get_db
from app.database.neo4j_db import get_driver


class XMLImporter:
    """
    Imports data from an XML file into both MongoDB and Neo4j.
    
    Usage:
        importer = XMLImporter("data/lms_data.xml")
        result = importer.import_all()
        print(result)  # Shows counts and any errors
    """
    
    def __init__(self, xml_path: str):
        """Initialize the importer with the path to the XML file."""
        self.xml_path = xml_path
        self.errors: List[str] = []
        self.mongo_counts = {
            "students": 0, "subjects": 0, "topics": 0, 
            "notes": 0, "comments": 0, "bookmarks": 0
        }
        self.neo4j_counts = {
            "nodes": 0, "relationships": 0
        }
    
    def import_all(self) -> dict:
        """
        Main import method - reads XML and writes to both databases.
        
        Returns a dictionary with:
        - success: bool
        - message: summary string
        - mongodb_counts: how many records were imported to MongoDB
        - neo4j_counts: how many nodes/relationships were created in Neo4j
        - errors: list of any errors encountered
        """
        try:
            # Step 1: Parse the XML file
            print(f"\n[XML] Parsing XML file: {self.xml_path}")
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            
            # Step 2: Extract data from XML into Python dictionaries
            students = self._parse_students(root)
            subjects = self._parse_subjects(root)
            topics = self._parse_topics(root)
            notes = self._parse_notes(root)
            relationships = self._parse_relationships(root)
            
            print(f"   Found: {len(students)} students, {len(subjects)} subjects, "
                  f"{len(topics)} topics, {len(notes)} notes")
            
            # Step 3: Import to MongoDB
            print("\n[MONGODB] Importing to MongoDB...")
            try:
                self._import_to_mongodb(students, subjects, topics, notes, relationships)
                print(f"   [OK] MongoDB import complete: {self.mongo_counts}")
            except Exception as e:
                error_msg = f"MongoDB import failed: {str(e)}"
                self.errors.append(error_msg)
                print(f"   [ERROR] {error_msg}")
            
            # Step 4: Import to Neo4j (even if MongoDB failed!)
            print("\n[NEO4J] Importing to Neo4j...")
            try:
                self._import_to_neo4j(students, subjects, topics, notes, relationships)
                print(f"   [OK] Neo4j import complete: {self.neo4j_counts}")
            except Exception as e:
                error_msg = f"Neo4j import failed: {str(e)}"
                self.errors.append(error_msg)
                print(f"   [ERROR] {error_msg}")
            
            # Step 5: Build result summary
            success = len(self.errors) == 0
            return {
                "success": success,
                "message": "Import completed successfully" if success else "Import completed with errors",
                "mongodb_counts": self.mongo_counts,
                "neo4j_counts": self.neo4j_counts,
                "errors": self.errors
            }
            
        except ET.ParseError as e:
            return {
                "success": False,
                "message": f"XML parsing error: {str(e)}",
                "mongodb_counts": self.mongo_counts,
                "neo4j_counts": self.neo4j_counts,
                "errors": [f"XML parse error: {str(e)}"]
            }
        except FileNotFoundError:
            return {
                "success": False,
                "message": f"XML file not found: {self.xml_path}",
                "mongodb_counts": self.mongo_counts,
                "neo4j_counts": self.neo4j_counts,
                "errors": [f"File not found: {self.xml_path}"]
            }
    
    # ==========================================
    # XML PARSING METHODS
    # ==========================================
    
    def _parse_students(self, root) -> List[dict]:
        """
        Parse <student> elements from XML into Python dictionaries.
        
        XML:  <student id="S101"><name>Arun</name>...</student>
        Dict: {"_id": "S101", "name": "Arun", ...}
        """
        students = []
        students_elem = root.find("students")
        if students_elem is None:
            return students
        
        for elem in students_elem.findall("student"):
            student_id = elem.get("id")
            if not student_id:
                self.errors.append("Found <student> without 'id' attribute - skipping")
                continue
            
            student = {
                "_id": student_id,
                "name": self._get_text(elem, "name", f"Student {student_id}"),
                "email": self._get_text(elem, "email", f"{student_id.lower()}@college.edu"),
                "department": self._get_text(elem, "department", "CSE"),
                "semester": int(self._get_text(elem, "semester", "1")),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Hash the password securely using bcrypt
            raw_password = self._get_text(elem, "password", "password123")
            student["password_hash"] = bcrypt.hashpw(
                raw_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            students.append(student)
        
        return students
    
    def _parse_subjects(self, root) -> List[dict]:
        """Parse <subject> elements from XML."""
        subjects = []
        subjects_elem = root.find("subjects")
        if subjects_elem is None:
            return subjects
        
        for elem in subjects_elem.findall("subject"):
            subject_id = elem.get("id")
            if not subject_id:
                self.errors.append("Found <subject> without 'id' attribute - skipping")
                continue
            
            subject = {
                "_id": subject_id,
                "name": self._get_text(elem, "name", f"Subject {subject_id}"),
                "code": self._get_text(elem, "code", subject_id),
                "department": self._get_text(elem, "department", "CSE"),
                "semester": int(self._get_text(elem, "semester", "1")),
            }
            subjects.append(subject)
        
        return subjects
    
    def _parse_topics(self, root) -> List[dict]:
        """Parse <topic> elements from XML."""
        topics = []
        topics_elem = root.find("topics")
        if topics_elem is None:
            return topics
        
        for elem in topics_elem.findall("topic"):
            topic_id = elem.get("id")
            if not topic_id:
                self.errors.append("Found <topic> without 'id' attribute - skipping")
                continue
            
            topic = {
                "_id": topic_id,
                "name": self._get_text(elem, "name", f"Topic {topic_id}"),
                "subjectId": elem.get("subjectId", ""),
                "description": self._get_text(elem, "description", ""),
            }
            topics.append(topic)
        
        return topics
    
    def _parse_notes(self, root) -> List[dict]:
        """Parse <note> elements from XML."""
        notes = []
        notes_elem = root.find("notes")
        if notes_elem is None:
            return notes
        
        for elem in notes_elem.findall("note"):
            note_id = elem.get("id")
            if not note_id:
                self.errors.append("Found <note> without 'id' attribute - skipping")
                continue
            
            # Parse tags: stored as comma-separated string in XML
            tags_text = self._get_text(elem, "tags", "")
            tags = [t.strip() for t in tags_text.split(",") if t.strip()]
            
            note = {
                "_id": note_id,
                "title": self._get_text(elem, "title", f"Note {note_id}"),
                "description": self._get_text(elem, "description", ""),
                "uploadedBy": elem.get("uploaderId", ""),
                "subjectId": elem.get("subjectId", ""),
                "topicId": elem.get("topicId", ""),
                "tags": tags,
                "fileUrl": self._get_text(elem, "fileUrl", ""),
                "likes": 0,
                "created_at": datetime.utcnow().isoformat()
            }
            notes.append(note)
        
        return notes
    
    def _parse_relationships(self, root) -> dict:
        """
        Parse <relationships> from XML.
        These define graph connections for Neo4j.
        
        Returns a dict with lists of each relationship type.
        """
        rels = {
            "prerequisites": [],
            "related_notes": [],
            "follows": [],
            "studies": [],
            "liked": [],
            "bookmarked": []
        }
        
        rels_elem = root.find("relationships")
        if rels_elem is None:
            return rels
        
        for elem in rels_elem.findall("prerequisite"):
            rels["prerequisites"].append({
                "from": elem.get("fromTopicId"),
                "to": elem.get("toTopicId")
            })
        
        for elem in rels_elem.findall("relatedNote"):
            rels["related_notes"].append({
                "from": elem.get("fromNoteId"),
                "to": elem.get("toNoteId")
            })
        
        for elem in rels_elem.findall("follows"):
            rels["follows"].append({
                "from": elem.get("fromStudentId"),
                "to": elem.get("toStudentId")
            })
        
        for elem in rels_elem.findall("studies"):
            rels["studies"].append({
                "studentId": elem.get("studentId"),
                "topicId": elem.get("topicId")
            })
        
        for elem in rels_elem.findall("liked"):
            rels["liked"].append({
                "studentId": elem.get("studentId"),
                "noteId": elem.get("noteId")
            })
        
        for elem in rels_elem.findall("bookmarked"):
            rels["bookmarked"].append({
                "studentId": elem.get("studentId"),
                "noteId": elem.get("noteId")
            })
        
        return rels
    
    def _get_text(self, parent, tag: str, default: str = "") -> str:
        """Safely get text content of a child element."""
        elem = parent.find(tag)
        if elem is not None and elem.text:
            return elem.text.strip()
        return default
    
    # ==========================================
    # MONGODB IMPORT METHODS
    # ==========================================
    
    def _import_to_mongodb(self, students, subjects, topics, notes, relationships):
        """
        Write parsed data to MongoDB collections.
        
        Uses 'update_one with upsert=True' to prevent duplicates:
        - If document with _id exists → update it
        - If document doesn't exist → insert it
        This makes the import safe to run multiple times!
        """
        db = get_db()
        
        # Import students
        for student in students:
            db["students"].update_one(
                {"_id": student["_id"]},      # Filter: find by _id
                {"$set": student},              # Update: set all fields
                upsert=True                      # Create if not exists
            )
            self.mongo_counts["students"] += 1
        
        # Import subjects
        for subject in subjects:
            db["subjects"].update_one(
                {"_id": subject["_id"]},
                {"$set": subject},
                upsert=True
            )
            self.mongo_counts["subjects"] += 1
        
        # Import topics
        for topic in topics:
            db["topics"].update_one(
                {"_id": topic["_id"]},
                {"$set": topic},
                upsert=True
            )
            self.mongo_counts["topics"] += 1
        
        # Import notes
        for note in notes:
            db["notes"].update_one(
                {"_id": note["_id"]},
                {"$set": note},
                upsert=True
            )
            self.mongo_counts["notes"] += 1
        
        # Import bookmarks from relationships
        for bm in relationships.get("bookmarked", []):
            bookmark_doc = {
                "_id": f"{bm['studentId']}_{bm['noteId']}",
                "studentId": bm["studentId"],
                "noteId": bm["noteId"],
                "created_at": datetime.utcnow().isoformat()
            }
            db["bookmarks"].update_one(
                {"_id": bookmark_doc["_id"]},
                {"$set": bookmark_doc},
                upsert=True
            )
            self.mongo_counts["bookmarks"] += 1
        
        # Update like counts on notes based on liked relationships
        like_counts = {}
        for liked in relationships.get("liked", []):
            note_id = liked["noteId"]
            like_counts[note_id] = like_counts.get(note_id, 0) + 1
        
        for note_id, count in like_counts.items():
            db["notes"].update_one(
                {"_id": note_id},
                {"$set": {"likes": count}}
            )
    
    # ==========================================
    # NEO4J IMPORT METHODS
    # ==========================================
    
    def _import_to_neo4j(self, students, subjects, topics, notes, relationships):
        """
        Create nodes and relationships in Neo4j.
        Uses MERGE instead of CREATE to prevent duplicates.
        """
        driver = get_driver()
        
        with driver.session() as session:
            # Create Subject nodes
            for subject in subjects:
                session.run(
                    "MERGE (s:Subject {subjectId: $id}) "
                    "SET s.name = $name, s.code = $code",
                    {"id": subject["_id"], "name": subject["name"], 
                     "code": subject.get("code", "")}
                )
                self.neo4j_counts["nodes"] += 1
            
            # Create Student nodes
            for student in students:
                session.run(
                    "MERGE (s:Student {studentId: $id}) "
                    "SET s.name = $name",
                    {"id": student["_id"], "name": student["name"]}
                )
                self.neo4j_counts["nodes"] += 1
            
            # Create Topic nodes + PART_OF relationships
            for topic in topics:
                session.run(
                    "MERGE (t:Topic {topicId: $id}) "
                    "SET t.name = $name",
                    {"id": topic["_id"], "name": topic["name"]}
                )
                self.neo4j_counts["nodes"] += 1
                
                if topic.get("subjectId"):
                    session.run(
                        "MATCH (t:Topic {topicId: $tid}), (s:Subject {subjectId: $sid}) "
                        "MERGE (t)-[:PART_OF]->(s)",
                        {"tid": topic["_id"], "sid": topic["subjectId"]}
                    )
                    self.neo4j_counts["relationships"] += 1
            
            # Create Note nodes + relationships
            for note in notes:
                session.run(
                    "MERGE (n:Note {noteId: $id}) "
                    "SET n.title = $title",
                    {"id": note["_id"], "title": note["title"]}
                )
                self.neo4j_counts["nodes"] += 1
                
                if note.get("uploadedBy"):
                    session.run(
                        "MATCH (s:Student {studentId: $sid}), (n:Note {noteId: $nid}) "
                        "MERGE (s)-[:UPLOADED]->(n)",
                        {"sid": note["uploadedBy"], "nid": note["_id"]}
                    )
                    self.neo4j_counts["relationships"] += 1
                
                if note.get("topicId"):
                    session.run(
                        "MATCH (n:Note {noteId: $nid}), (t:Topic {topicId: $tid}) "
                        "MERGE (n)-[:ABOUT]->(t)",
                        {"nid": note["_id"], "tid": note["topicId"]}
                    )
                    self.neo4j_counts["relationships"] += 1
            
            # Create PREREQUISITE_OF relationships
            for prereq in relationships.get("prerequisites", []):
                session.run(
                    "MATCH (t1:Topic {topicId: $from}), (t2:Topic {topicId: $to}) "
                    "MERGE (t1)-[:PREREQUISITE_OF]->(t2)",
                    {"from": prereq["from"], "to": prereq["to"]}
                )
                self.neo4j_counts["relationships"] += 1
            
            # Create RELATED_TO relationships
            for rel in relationships.get("related_notes", []):
                session.run(
                    "MATCH (n1:Note {noteId: $from}), (n2:Note {noteId: $to}) "
                    "MERGE (n1)-[:RELATED_TO]->(n2)",
                    {"from": rel["from"], "to": rel["to"]}
                )
                self.neo4j_counts["relationships"] += 1
            
            # Create FOLLOWS relationships
            for follow in relationships.get("follows", []):
                session.run(
                    "MATCH (s1:Student {studentId: $from}), (s2:Student {studentId: $to}) "
                    "MERGE (s1)-[:FOLLOWS]->(s2)",
                    {"from": follow["from"], "to": follow["to"]}
                )
                self.neo4j_counts["relationships"] += 1
            
            # Create STUDIES relationships
            for study in relationships.get("studies", []):
                session.run(
                    "MATCH (s:Student {studentId: $sid}), (t:Topic {topicId: $tid}) "
                    "MERGE (s)-[:STUDIES]->(t)",
                    {"sid": study["studentId"], "tid": study["topicId"]}
                )
                self.neo4j_counts["relationships"] += 1
            
            # Create LIKED relationships
            for liked in relationships.get("liked", []):
                session.run(
                    "MATCH (s:Student {studentId: $sid}), (n:Note {noteId: $nid}) "
                    "MERGE (s)-[:LIKED]->(n)",
                    {"sid": liked["studentId"], "nid": liked["noteId"]}
                )
                self.neo4j_counts["relationships"] += 1
            
            # Create BOOKMARKED relationships
            for bm in relationships.get("bookmarked", []):
                session.run(
                    "MATCH (s:Student {studentId: $sid}), (n:Note {noteId: $nid}) "
                    "MERGE (s)-[:BOOKMARKED]->(n)",
                    {"sid": bm["studentId"], "nid": bm["noteId"]}
                )
                self.neo4j_counts["relationships"] += 1


def run_import(xml_path: str = None) -> dict:
    """
    Convenience function to run the XML import.
    Can be called from the API route or from the command line.
    """
    if xml_path is None:
        xml_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "lms_data.xml"
        )
    
    importer = XMLImporter(xml_path)
    return importer.import_all()
