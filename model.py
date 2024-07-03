from database import create_table
import uvicorn



class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

if __name__ == "__main__":
    create_table()
    uvicorn.run(app, host="0.0.0.0", port=8000)