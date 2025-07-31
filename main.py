from fastapi import FastAPI
from datetime import datetime
from Models.User import User

app = FastAPI()

@app.get("/")
async def first_step():
    return {"message": "Hello Finance World!"}

@app.get("/user/me")
async def get_user_me():
    me = {
        "id" : 1,
        "name" : "John doe",
        "email" : "johndoe@123@gmail.com",
        "age" : 18,
        "currency" : "INR",
        "location" : "India",
        "date_create" : datetime.now().isoformat()
    }
    return me


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
 