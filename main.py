import uvicorn
from app.main import app

"""
This is the entry point for the application.
Run the project using: python main.py
Or via uvicorn: uvicorn main:app --reload
"""

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)