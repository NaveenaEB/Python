from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import user_schema
from app.repositories import user_repository
from app.services import user_service
from app.core import security
from app.core.database import get_db
import logging

logger = logging.getLogger("uvicorn.error")

router = APIRouter()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    #  (Strip quotes if present)
    # Clean up the token string. 
    # We strip whitespace, quotes, and the "Bearer " prefix if it was accidentally double-added.
    if token:
        print(f"DEBUG: get_current_user called with token: {token[:20]}...")
    actual_token = token.replace("Bearer ", "").strip().strip('"').strip("'")
    
    if not actual_token:
        print("DEBUG: Token is empty after cleanup")
        raise credentials_exception
    payload = security.verify_token(actual_token)
    
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = user_repository.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@router.post("", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    return user_service.register_user(db=db, user=user)

@router.get("", response_model=List[user_schema.User], dependencies=[Depends(get_current_user)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=user_schema.User, dependencies=[Depends(get_current_user)])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_profile(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=user_schema.User, dependencies=[Depends(get_current_user)])
def update_user(user_id: int, user: user_schema.UserUpdate, db: Session = Depends(get_db)):
    db_user = user_service.update_existing_user(db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.delete("/{user_id}", dependencies=[Depends(get_current_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = user_service.remove_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted successfully"}