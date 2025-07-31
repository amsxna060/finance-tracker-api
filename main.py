from fastapi import FastAPI
from datetime import datetime
from Models.User import User

app = FastAPI()

@app.get("/")
async def first_step():
    return {"message": "Hello Finance World!"}

@app.get("/user/me")
async def get_user_me():
    me = User()
    return {"user" : me}


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
 