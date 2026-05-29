from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse
import os

# Replace with your actual MySQL credentials
password = urllib.parse.quote_plus("Lsp@12345")
DEFAULT_URL = f"mysql+pymysql://root:{password}@localhost:3306/blogApplication"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()