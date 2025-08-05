"""
Database session management for SQLAlchemy.
This module provides session handling and dependency injection for FastAPI.
"""

from .connection import SessionLocal
from typing import Generator

def get_db() -> Generator:
    """
    Dependency to get database session for FastAPI endpoints.
    This function yields a database session and ensures it's properly closed.
    
    Usage in FastAPI endpoints:
        @app.post("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
