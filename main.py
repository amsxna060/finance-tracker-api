from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from sqlalchemy.orm import Session
from Models.User import User
from Models.UserCreate import UserCreate
from Models.LoginRequest import LoginRequest
from util import verify_password,get_password_hash,create_access_token,verify_token
from database import create_tables, get_db, User as DBUser

app = FastAPI(
     title="FINANCE TARCKER API",
     description="This api is handle user finance data and trasactiona and expenses."
     )

# Add this after app creation
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("✅ Database tables created successfully!")

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
    
    # Find user by email from token
    user_email = payload.get("email")
    db_user = db.query(DBUser).filter(DBUser.email == user_email).first()
    if db_user:
        return User.model_validate(db_user)
            
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )

@app.get("/",summary="Root Endpoint")
async def read_root():
    return {"message": "Finance Tracker API - LIVE UPDATES WORK!", "status": "running", "version": "1.0.0"}

@app.get("/user/me")
async def get_user_me(current_user: User = Depends(get_current_user)):
    user_data = current_user.model_dump()
    user_data['password'] = None  # Don't return password
    return user_data

@app.post('/register')
async def registration(new_user: UserCreate, db: Session = Depends(get_db)):
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
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Convert to Pydantic model for response
    user_response = User.model_validate(db_user)
    user_response.password = None  # Don't return password
    
    return {
        "status": status.HTTP_201_CREATED,
        "added_user": user_response.model_dump()
    }

@app.post('/login')
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(DBUser).filter(DBUser.email == login_request.email).first()
    
    if not db_user:
        return {
            'status': status.HTTP_404_NOT_FOUND,
            'description': 'No user found!'
        }
    
    # Verify password
    if not verify_password(login_request.password, db_user.password):
        return {
            'status': status.HTTP_401_UNAUTHORIZED,
            'description': 'Login failed due to Wrong Password'
        }
    
    # Create JWT token with user data
    token_data = {
        "user_id": db_user.id,
        "email": db_user.email
    }
    access_token = create_access_token(data=token_data)
    
    # Return success with real JWT
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
    db_users = db.query(DBUser).all()
    users = []
    for db_user in db_users:
        user = User.model_validate(db_user)
        user.password = None  # Don't return passwords
        users.append(user)
    
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
 