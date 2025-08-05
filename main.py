from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from Models.User import User
from Models.UserCreate import UserCreate
from Models.LoginRequest import LoginRequest
from util import verify_password,get_password_hash,create_access_token,verify_token

app = FastAPI(
     title="FINANCE TARCKER API",
     description="This api is handle user finance data and trasactiona and expenses."
     )

fake_users_db = []

# Add this after your imports, before the routes
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
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
    for user in fake_users_db:
        if user.email == user_email:
            return user
            
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )

@app.get("/",summary="Root Endpoint")
async def read_root():
    return {"message": "Finance Tracker API - LIVE UPDATES WORK!", "status": "running", "version": "1.0.0"}

@app.get("/user/me")
async def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user.model_dump()

@app.post('/register')
async def registration(new_user : UserCreate):
        user = User(
             id = len(fake_users_db)+1,
             name= new_user.name,
             email=new_user.email,
             age=new_user.age,
             gender=new_user.gender,
             password=get_password_hash(new_user.password),
             is_verified=False,
             currency='INR',
             location='India',
             date_created=datetime.now().isoformat(),
             date_updated=datetime.now().isoformat()   
        )

        fake_users_db.append(user)

        return {
             "status": status.HTTP_201_CREATED,
             "added_user":user.model_dump()
        }

@app.post('/login')
async def login(login_request: LoginRequest ):
     email_list_of_user = {user.email:user.password for user in fake_users_db}
     if login_request.email in email_list_of_user.keys():
          if verify_password(login_request.password,email_list_of_user[login_request.email]):
            # Step 2: Find the actual user object (you need this!)
            current_user:User|None = None
            for user in fake_users_db:
                if user.email == login_request.email:
                    current_user = user
                    break
            # Step 3: Create JWT token with user data
            token_data = {
                "user_id": current_user.id,
                "email": current_user.email
            }
            access_token = create_access_token(data=token_data)
            # Step 4: Return success with real JWT
            return {
                'status': status.HTTP_200_OK,
                'access_token': access_token,
                'token_type': 'bearer',
                'user': {
                    'id': current_user.id,
                    'name': current_user.name,
                    'email': current_user.email
                }
            }
          else:
               return {
                    'status': status.HTTP_401_UNAUTHORIZED,
                    'description':'Login failed due to Wrong Password'
               }
     else:
          return {
               'status': status.HTTP_404_NOT_FOUND,
               'description':'No user found!'
          }
          



          
@app.get('/users')   
async def get_all_user():
    return {
        'status':status.HTTP_200_OK,
        'users':fake_users_db
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
 