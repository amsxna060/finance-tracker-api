"""
Database connection setup for SQLite using SQLAlchemy.
This module provides the database engine and connection configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite database file path
DATABASE_URL = "sqlite:///./finance_tracker.db"

# Create SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed for SQLite with FastAPI
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query logging during development
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for SQLAlchemy models
Base = declarative_base()

def create_tables():
    """
    Create all database tables defined by SQLAlchemy models.
    This should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
