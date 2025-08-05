from sqlalchemy.orm import Session
from database.connection import SessionLocal, engine
from database.models.user import Base

def get_db():
    """
    Database session dependency for FastAPI
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables in the database
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def drop_tables():
    """
    Drop all tables (useful for development)
    """
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Database tables dropped successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to drop tables: {e}")
        return False
