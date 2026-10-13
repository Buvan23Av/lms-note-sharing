"""
config.py - Application Configuration
======================================
Loads settings from .env file using python-dotenv.
All database URLs, secrets, and app settings live here.
Never hardcode passwords in your code - always use environment variables!
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Central configuration class that reads from environment variables."""
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "lms_db")
    
    # Neo4j settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password123")
    
    # JWT settings for authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "my_super_secret_key_for_student_project")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
    
    # Upload settings
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".png", ".jpg"}


# Create a single settings instance used throughout the app
settings = Settings()
