from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

# Import database components
from database import create_tables, get_db, test_connection
from database.models import User as DBUser

# Import Pydantic models
from Models.User import User, UserResponse
from Models.UserCreate import UserCreate
from Models.LoginRequest import LoginRequest
from util import verify_password, get_password_hash, create_access_token, verify_token

app = FastAPI(
    title="FINANCE TRACKER API",
    description="This API handles user finance data, transactions and expenses.",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Database startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    print("🚀 Starting Finance Tracker API...")
    
    # Test database connection
    if test_connection():
        # Create tables
        if create_tables():
            print("🎉 Database initialized successfully!")
        else:
            print("❌ Failed to initialize database!")
    else:
        print("❌ Database connection failed!")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency to get current user from JWT token using database
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Find user by email from database
    user_email = payload.get("email")
    db_user = db.query(DBUser).filter(DBUser.email == user_email).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return db_user

@app.get("/", summary="Root Endpoint")
async def root():
    return {"message": "Hello Finance World! 🚀"}

@app.get("/user/me", response_model=UserResponse)
async def get_user_me(current_user: DBUser = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@app.post('/register', response_model=UserResponse)
async def registration(new_user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(DBUser).filter(DBUser.email == new_user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = DBUser(
        name=new_user.name,
        email=new_user.email,
        age=new_user.age,
        gender=new_user.gender,
        password=get_password_hash(new_user.password),
        is_verified=False,
        currency='INR',
        location='India'
    )
    
    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post('/login')
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """User login"""
    
    # Find user by email
    db_user = db.query(DBUser).filter(DBUser.email == login_request.email).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify password
    if not verify_password(login_request.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Create JWT token
    token_data = {
        "user_id": db_user.id,
        "email": db_user.email
    }
    access_token = create_access_token(data=token_data)
    
    return {
        'status': status.HTTP_200_OK,
        'access_token': access_token,
        'token_type': 'bearer',
        'user': {
            'id': db_user.id,
            'name': db_user.name,
            'email': db_user.email
        }
    }

@app.get('/users', response_model=list[UserResponse])   
async def get_all_users(db: Session = Depends(get_db)):
    """Get all users (admin endpoint)"""
    users = db.query(DBUser).all()
    return users

@app.get("/health")
async def health_check():
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "API is Running",
        "database": "Connected"
    }

@app.get("/version")
async def get_version():
    return {
        "version": "1.0.0",
        "description": "Finance Tracker API with SQLAlchemy integration"
    }
