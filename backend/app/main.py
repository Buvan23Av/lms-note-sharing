"""
main.py - FastAPI Application Entry Point
==========================================
This is where the FastAPI app is created and configured.

What happens when you run the server:
1. FastAPI app is created
2. CORS middleware is added (allows React frontend to talk to this API)
3. On startup: connects to MongoDB and Neo4j
4. On shutdown: closes database connections
5. API routes are registered
6. Swagger docs available at http://localhost:8000/docs

Run with: uvicorn app.main:app --reload --port 8000
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Import database connection functions
from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.neo4j_db import connect_neo4j, close_neo4j

# Import route modules
from app.routes import students, notes, search, integration


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager - runs code on startup and shutdown.
    
    Startup: Connect to both databases
    Shutdown: Close all connections cleanly
    """
    # === STARTUP ===
    print("\n" + "="*50)
    print("[SERVER] Starting LMS Backend Server")
    print("="*50)
    
    # Connect to MongoDB
    mongo_db = connect_mongodb()
    if mongo_db is None:
        print("[WARN] MongoDB not available - some features will not work")
    
    # Connect to Neo4j
    neo4j_driver = connect_neo4j()
    if neo4j_driver is None:
        print("[WARN] Neo4j not available - graph features will not work")
    
    print("="*50)
    print("[READY] Server ready! Open http://localhost:8000/docs for Swagger UI")
    print("="*50 + "\n")
    
    yield  # Server runs here
    
    # === SHUTDOWN ===
    print("\nShutting down...")
    close_mongodb()
    close_neo4j()
    print("Goodbye!")


# Create the FastAPI application
app = FastAPI(
    title="LMS - Note Sharing System",
    description=(
        "A Learning Management System that uses MongoDB for document storage "
        "and Neo4j for relationship graphs. Demonstrates multi-database "
        "integration with XML data import."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# === CORS Middleware ===
# This allows the React frontend (running on port 5173) to call this API.
# Without CORS, the browser would block requests from a different port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)

# === Mount uploads directory ===
# This serves uploaded files (PDFs, docs) as static files
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# === Register API Routes ===
# Each route module handles a specific area of the API
app.include_router(students.router, prefix="/api", tags=["Students"])
app.include_router(notes.router, prefix="/api", tags=["Notes"])
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(integration.router, prefix="/api", tags=["Integration"])


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint - verify the server is running."""
    return {
        "message": "LMS API is running!",
        "docs": "http://localhost:8000/docs",
        "version": "1.0.0"
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    """
    Check if both databases are connected.
    Useful for debugging connection issues.
    """
    from app.database.mongodb import get_db
    from app.database.neo4j_db import get_driver
    
    status = {"mongodb": "disconnected", "neo4j": "disconnected"}
    
    try:
        db = get_db()
        db.command('ping')
        status["mongodb"] = "connected"
    except Exception:
        pass
    
    try:
        driver = get_driver()
        driver.verify_connectivity()
        status["neo4j"] = "connected"
    except Exception:
        pass
    
    return status
