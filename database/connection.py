from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# 🔥 ADD THESE FUNCTIONS:

def create_tables():
    """Create all tables in the database."""
    # Import all models so they're registered with Base
    from database.models import User, Account, Category, Transaction
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def drop_tables():
    """Drop all tables in the database. USE WITH CAUTION!"""
    from database.models import User, Account, Category, Transaction
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped!")