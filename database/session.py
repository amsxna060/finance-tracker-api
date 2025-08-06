from database.connection import SessionLocal

def get_db():
    """
    Dependency function to get a DB session that automatically closes
    when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()