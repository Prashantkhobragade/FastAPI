from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from database import connect_to_database, execute_create_queries, execute_query, insert_into_table

app = FastAPI()


class UserRequest(BaseModel):
    username: str
    email: str


@app.get("/provision")
def provision(request: Request):
    create_queries = ["""
        # Create table queries
            CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL
                );"""
    ]

    connection = connect_to_database()

    if connection:
        execute_create_queries(connection, create_queries)
        return HTMLResponse("Provisioning completed and PostgreSQL connection is closed")
    else:
        return HTMLResponse("Error creating Db connection")

@app.post("/run-query")
async def run_query(request: Request):
    try:
        query_data = await request.json()
        query = query_data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is missing")

        connection = connect_to_database()
        result = execute_query(connection, query)
        return HTMLResponse(content=result)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An error occurred: {error}")
    

@app.post("/user")
async def create_user(user: UserRequest):
    try:
        insert_into_table(user)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))