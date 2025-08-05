from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Import your models
from Models.User import User, UserResponse
from Models.UserCreate import UserCreate
from Models.LoginRequest import LoginRequest

# Import database components
from database import create_tables, get_db, test_connection
from database.models import User as DBUser

from util import verify_password, get_password_hash, create_access_token, verify_token

app = FastAPI(
    title="FINANCE TRACKER API",
    description="This API handles user finance data, transactions and expenses."
)

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    print("🚀 Starting Finance Tracker API...")
    
    # Test database connection
    if test_connection():
        # Create tables
        create_tables()
        print("📊 Database initialization complete!")
    else:
        print("❌ Database initialization failed!")

# Add this after your imports, before the routes
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
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
    
    # Find user by email from token using database
    user_email = payload.get("email")
    user = db.query(DBUser).filter(DBUser.email == user_email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@app.get("/", summary="Root Endpoint")
async def first_step():
    return {"message": "Hello Finance World!"}

@app.get("/user/me", response_model=UserResponse)
async def get_user_me(current_user: DBUser = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@app.post('/register', response_model=UserResponse)
async def registration(new_user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user using database"""
    try:
        # Create new user instance
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
        db.refresh(db_user)  # Get the ID and timestamps
        
        return db_user
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post('/login')
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """Login user using database"""
    # Find user by email
    user = db.query(DBUser).filter(DBUser.email == login_request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    # Verify password
    if not verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password'
        )
    
    # Create JWT token
    token_data = {
        "user_id": user.id,
        "email": user.email
    }
    access_token = create_access_token(data=token_data)
    
    return {
        'status': status.HTTP_200_OK,
        'access_token': access_token,
        'token_type': 'bearer',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }
    }
          



          
@app.get('/users', response_model=list[UserResponse])
async def get_all_users(db: Session = Depends(get_db)):
    """Get all users from database"""
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
        "description": "This is the version endpoint of the Finance API."
    }
 