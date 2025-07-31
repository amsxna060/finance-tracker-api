from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
async def first_step():
    return {"message": "Hello Finance World!"}

@app.get("/health")
def health_check():
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "Api is Running"
    }

@app.get("/version")
def get_version():
    return {
        "version" : "1.0.0",
        "description": "This is the version endpoint of the Finance API."
    }
 