from fastapi import FastAPI
from datetime import datetime
from Models.User import User
from Models.UserCreate import UserCreate
from util import verify_password,get_password_hash

app = FastAPI(
     title="FINANCE TARCKER API",
     description="This api is handle user finance data and trasactiona and expenses."
     )

fake_users_db = []

@app.get("/",summary="Root Endpoint")
async def first_step():
    return {"message": "Hello Finance World!"}

@app.get("/user/me")
async def get_user_me():
    me = User(id=1,name="amol",email="amolsaxena123@gmail.com",age=25,gender="M",password="********",currency="INR",location="India")
    return me.model_dump()

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
             "status": "successful",
             "added_user":user.model_dump()
        }

@app.get("/health")
async def health_check():
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "Api is Running"
    }

@app.get("/version")
async def get_version():
    return {
        "version" : "1.0.0",
        "description": "This is the version endpoint of the Finance API."
    }
 