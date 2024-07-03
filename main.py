from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_table, insert_into_table
from model import User

app = FastAPI()

class UserRequest(BaseModel):
    username: str
    email: str

@app.post("/users/")
async def create_user(user: UserRequest):
    try:
        user_object = User(username=user.username, email=user.email)
        insert_into_table(user_object)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/")
async def get_users():
    try:
        users = []
        # TO DO: implement fetching users from database
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))