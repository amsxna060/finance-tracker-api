from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from Models.User import User as PydanticUser
from Models.UserCreate import UserCreate
from Models.LoginRequest import LoginRequest
from database.session import get_db
from database.connection import create_tables
from database.models.user import User as DBUser
from util import verify_password, get_password_hash, create_access_token, verify_token

app = FastAPI(
     title="FINANCE TARCKER API",
     description="This api is handle user finance data and trasactiona and expenses."
     )

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Create database tables when the application starts"""
    create_tables()

# Remove fake_users_db as we're now using a real database

# Add this after your imports, before the routes
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Dependency to get current user from JWT token
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
    db_user = db.query(DBUser).filter(DBUser.email == user_email).first()
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return db_user

@app.get("/",summary="Root Endpoint")
async def read_root():
    return {"message": "Finance Tracker API - LIVE UPDATES WORK!", "status": "running", "version": "1.0.0"}

@app.get("/user/me")
async def get_user_me(current_user: DBUser = Depends(get_current_user)):
    # Convert SQLAlchemy model to Pydantic model for response
    return PydanticUser.model_validate(current_user)

@app.post('/register')
async def registration(new_user: UserCreate, db: Session = Depends(get_db)):
        # Check if user already exists
        existing_user = db.query(DBUser).filter(DBUser.email == new_user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new database user
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

        # Convert to Pydantic model for response
        pydantic_user = PydanticUser.model_validate(db_user)

        return {
             "status": status.HTTP_201_CREATED,
             "added_user": pydantic_user.model_dump()
        }

@app.post('/login')
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
     # Find user by email in database
     db_user = db.query(DBUser).filter(DBUser.email == login_request.email).first()
     
     if db_user is None:
          return {
               'status': status.HTTP_404_NOT_FOUND,
               'description':'No user found!'
          }
     
     # Verify password
     if not verify_password(login_request.password, db_user.password):
          return {
                'status': status.HTTP_401_UNAUTHORIZED,
                'description':'Login failed due to Wrong Password'
          }
     
     # Create JWT token with user data
     token_data = {
         "user_id": db_user.id,
         "email": db_user.email
     }
     access_token = create_access_token(data=token_data)
     
     # Return success with JWT token
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
          



          
@app.get('/users')   
async def get_all_user(db: Session = Depends(get_db)):
    # Get all users from database
    db_users = db.query(DBUser).all()
    
    # Convert to Pydantic models for response
    users = [PydanticUser.model_validate(user) for user in db_users]
    
    return {
        'status': status.HTTP_200_OK,
        'users': [user.model_dump() for user in users]
    }   
          


@app.get("/health")
async def health_check():
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "Api is Running with Live updates..."
    }

@app.get("/version")
async def get_version():
    return {
        "version" : "1.0.0",
        "description": "This is the version endpoint of the Finance API."
    }
 