from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from Models.User import User
from Models.UserResponse import UserResponse
from database.models import User as DBUser
from database.models.user import Gender, Role
from Models.UserCreate import UserCreate
from Models.LoginRequest import LoginRequest
from sqlalchemy.orm import Session
from database.session import get_db
from util import verify_password,get_password_hash,create_access_token,verify_token
from auth.permissions import get_current_user, require_auth
from routers import admin,account

app = FastAPI(
     title="FINANCE TARCKER API",
     description="This api is handle user finance data and trasactiona and expenses."
     )

# Add this after your imports, before the routes
security = HTTPBearer()

# Include admin router
app.include_router(admin.router)
app.include_router(account.router)

@app.get("/",summary="Root Endpoint")
async def read_root():
    return {"message": "Finance Tracker API - LIVE UPDATES WORK!", "status": "running", "version": "1.0.0"}

@app.get("/user/me")
async def get_user_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@app.post('/register')
async def registration(new_user : UserCreate, db : Session = Depends(get_db)):
        
        #first check if user is in database already
        existing_user = db.query(DBUser).filter(DBUser.email == new_user.email).first()

        if existing_user :
            raise HTTPException(status.HTTP_400_BAD_REQUEST,"User Already Exist")
        
        hashed_password = get_password_hash(new_user.password)
        user = DBUser(
             name= new_user.name,
             email=new_user.email,
             password=hashed_password,
             age= getattr(new_user,'age',None),
             gender=getattr(new_user,'gender',Gender.MALE),
             role=getattr(new_user,'role',Role.USER),  # Add role with default
             is_verified=getattr(new_user,'is_verified',False),
             currency=getattr(new_user,'currency','INR'),
             location=getattr(new_user,'location','India'), 
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
        return {
             "status": status.HTTP_201_CREATED,
             "message": "User Created Successfully",
             "user": {
                 "name":user.name,
                 "email":user.email
             }
        }

@app.post('/login')
async def login(login_request: LoginRequest , db : Session = Depends(get_db)):
     # try to fetch the user 
     user = db.query(DBUser).filter(DBUser.email==login_request.email).first()
     if not user :
         raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Not Have Account, please Sign Up!!")
     
     # Step 2: Verify Password
     if verify_password(login_request.password,user.password):
        # Step 3: Create JWT token with user data
        token_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role.value  # Add role to JWT token
        }
        access_token = create_access_token(data=token_data)
        # Step 4: Return success with real JWT
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

     else:
         raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Wrong Password!!")

           

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
 