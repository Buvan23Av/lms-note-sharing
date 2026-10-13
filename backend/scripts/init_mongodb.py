"""
init_mongodb.py - Initialize MongoDB with Sample Data
=====================================================
Run this script to populate MongoDB with sample data from the XML file.

Usage: 
    cd backend
    python -m scripts.init_mongodb
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.mongodb import connect_mongodb, get_db
from app.database.neo4j_db import connect_neo4j
from app.services.xml_importer import run_import


def main():
    print("\n" + "="*50)
    print("[INIT] MongoDB + Neo4j Initialization Script")
    print("="*50)
    
    mongo_db = connect_mongodb()
    if mongo_db is None:
        print("\n[ERROR] Cannot proceed without MongoDB. Is it running?")
        print("        Try: docker-compose up -d")
        sys.exit(1)
    
    neo4j_driver = connect_neo4j()
    if neo4j_driver is None:
        print("\n[WARN] Neo4j not available. Will only import to MongoDB.")
    
    db = get_db()
    existing_notes = db["notes"].count_documents({})
    
    if existing_notes > 0:
        print(f"\n[INFO] Found {existing_notes} existing notes in MongoDB.")
        print("       The import uses upsert, so existing data will be updated.")
        # Default to updating rather than blocking on interactive prompt if piped
        try:
            response = input("       Do you want to DROP all collections first? (y/N): ").strip().lower()
            if response == 'y':
                for coll in ["students", "subjects", "topics", "notes", "comments", "bookmarks"]:
                    db[coll].drop()
                    print(f"       Dropped collection: {coll}")
        except EOFError:
            pass
    
    print("\n[IMPORT] Starting XML import...")
    result = run_import()
    
    print("\n" + "="*50)
    print("[SUMMARY] Import Results")
    print("="*50)
    print(f"  Status:  {'[OK] Success' if result['success'] else '[FAILED]'}")
    print(f"  Message: {result['message']}")
    print(f"\n  MongoDB Counts:")
    for key, count in result['mongodb_counts'].items():
        print(f"    {key}: {count}")
    print(f"\n  Neo4j Counts:")
    for key, count in result['neo4j_counts'].items():
        print(f"    {key}: {count}")
    
    if result['errors']:
        print(f"\n  [ERRORS]:")
        for err in result['errors']:
            print(f"    - {err}")
    
    print(f"\n  Final MongoDB Collection Counts:")
    for coll_name in ["students", "subjects", "topics", "notes", "comments", "bookmarks"]:
        count = db[coll_name].count_documents({})
        print(f"    {coll_name}: {count}")
    
    print("\n[COMPLETE] Initialization complete!")
    print("   Start the server with: uvicorn app.main:app --reload --port 8000")
    print("   Open Swagger UI at: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
