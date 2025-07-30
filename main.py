from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def first_step():
    return {"message": "Hello Finance World!"}