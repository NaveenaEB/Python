from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import user_schema
from app.repositories import user_repository
from app.services import user_service
from app.core import security
from app.core.database import get_db

router = APIRouter()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    #  (Strip quotes if present)
    token = token.strip('"').strip("'")

    # "Bearer <token>" 
    if not token.startswith("Bearer "):
        raise credentials_exception
        
    actual_token = token.replace("Bearer ", "")
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

@router.post("/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    return user_service.register_user(db=db, user=user)

@router.get("/", response_model=List[user_schema.User], dependencies=[Depends(get_current_user)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_service.get_all_users(db, skip=skip, limit=limit)

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