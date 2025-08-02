from fastapi import FastAPI
from datetime import datetime
from Models.User import User

app = FastAPI()
user_list = []
@app.get("/")
async def first_step():
    return {"message": "Hello Finance World!"}

@app.get("/user/me")
async def get_user_me():
    me = User(id=1,name="amol",email="amolsaxena123@gmail.com",age=25,gender="M",password="********",currency="INR",location="India")
    return me.model_dump()

@app.post('/register')
async def registration(user : User):
        user_list.append(user)
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
 