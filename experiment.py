from fastapi import FastAPI, HTTPException, Request
import json
from pydantic import BaseModel

app = FastAPI()

class UserRequest(BaseModel):
    username: str
    email: str

# Mock function to simulate table creation
def execute_create_queries():
    print("Simulating table creation...")
    create_queries = ["""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL
        );
    """]
    for query in create_queries:
        print(f"Query executed: {query}")
    print("All create queries executed successfully")

# Mock function to simulate query execution
def execute_query(query):
    print(f"Executing query: {query}")
    # Simulate result for SELECT query
    if "SELECT" in query:
        result = [("example_user", "example_user@example.com")]
        result_json = json.dumps(result)
        return result_json
    else:
        return "Query executed successfully"

# Mock function to simulate inserting into table
def insert_into_table(user):
    print(f"Inserting into table: username={user.username}, email={user.email}")
    print("User created successfully")


@app.get("/provision")
def provision():
    try:
        execute_create_queries()
        return {"message": "Provising completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


## This is not working need to debug
@app.post("/run-query")
async def run_query(request: Request):
    print(f"Request method : {request.method}")
    try:
        query_data = await request.json()
        query = query_data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query not provided")
        
        result = execute_query(query)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#this is not working need to debug
@app.post("/user")
async def create_user(user: UserRequest):
    print(f"Request method : {Request.method}")
    try:
        insert_into_table(user)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
""""
if __name__ == "__main__":
    try:
        # Simulate provisioning: Create tables
        execute_create_queries()
        print("Provisioning completed")

        # Insert user example
        user = UserRequest(username="example_user", email="example_user@example.com")
        insert_into_table(user)

        # Run a sample query
        query = "SELECT * FROM users;"
        result = execute_query(query)
        print("Query result:", result)

    except Exception as e:
        print(f"An error occurred: {e}")
"""