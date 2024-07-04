import os
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