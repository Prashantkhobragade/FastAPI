#database.py
import os
import json
import psycopg2
from psycopg2 import pool
from cfenv import AppEnv
from fastapi import HTTPException

def connect_to_database():
    try:
        env = AppEnv()
        sql_service = 'postgresql-db'
        sql = env.get_service(label=sql_service)
        db_credentials = {
            "user": sql.credentials['username'],
            "password": sql.credentials['password'],
            "host": sql.credentials['hostname'],
            "port": sql.credentials['port'],
            "database": sql.credentials['dbname']
        }
        
        connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, **db_credentials)
        if connection_pool:
            connection = connection_pool.getconn()
            return connection
        else:
            raise HTTPException(status_code=500, detail="Error creating connection pool")
    except (Exception, psycopg2.Error) as error:
        raise HTTPException(status_code=500, detail=f"Error Connecting to DB: {error}")

def execute_create_queries(connection, create_queries):
    try:
        cursor = connection.cursor()

        for query in create_queries:
            cursor.execute(query)
            print(f"Query executed: {query}")

        connection.commit()
        print("All create queries executed successfully")
    except (Exception, psycopg2.Error) as error:
        raise HTTPException(status_code=500, detail=f"Error executing query: {error}")
    finally:
        if cursor:
            cursor.close()
        connection_pool.putconn(connection)

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        if cursor.description:
            result = cursor.fetchall()
            result_json = json.dumps(result)
            return result_json
        else:
            return "Query executed successfully"
    except psycopg2.Error as error:
        raise HTTPException(status_code=500, detail=f"Error executing query: {error}")
    finally:
        cursor.close()
        connection_pool.putconn(connection)

def insert_into_table(user):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, email)
            VALUES (%s, %s);
            """, (user.username, user.email)
        )
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        raise HTTPException(status_code = 500, detail= f"Error inserting into table: {error}")
    finally:
        if cursor:
            cursor.close()
        connection_pool.putconn(connection)


#main.py
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