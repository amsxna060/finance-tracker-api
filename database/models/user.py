"""
SQLAlchemy User model for the finance tracker application.
This model defines the database schema for user data.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..connection import Base

class User(Base):
    """
    SQLAlchemy User model representing users in the finance tracker.
    
    Fields match the Pydantic User model for consistency:
    - id: Primary key, auto-incrementing integer
    - name: User's full name
    - email: User's email address (should be unique)
    - age: User's age
    - gender: User's gender
    - password: Hashed password
    - is_verified: Boolean flag for email verification
    - currency: User's preferred currency (default: 'INR')
    - location: User's location (default: 'India')
    - created_at: Timestamp when user was created
    - updated_at: Timestamp when user was last updated
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    password = Column(String, nullable=False)  # This will store hashed passwords
    is_verified = Column(Boolean, default=False, nullable=False)
    currency = Column(String, default='INR', nullable=False)
    location = Column(String, default='India', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
