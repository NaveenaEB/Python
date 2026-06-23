from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.features.users import schema as user_schema
from app.common.schemas.api_response import ApiResponse
from app.features.users import repository as user_repository
from app.features.users import service as user_service
from app.common.exceptions.custom_exceptions import EntityNotFoundException
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

@router.post("", response_model=ApiResponse[user_schema.User], status_code=status.HTTP_201_CREATED)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    data = user_service.register_user(db=db, user=user)
    return ApiResponse(data=data, isSuccess=True, message="User registered successfully.")

@router.get("", response_model=ApiResponse[List[user_schema.User]], dependencies=[Depends(get_current_user)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return ApiResponse(data=users, isSuccess=True, message="Users retrieved successfully.")

@router.get("/me", response_model=ApiResponse[user_schema.User])
def read_current_user(current_user = Depends(get_current_user)):
    return ApiResponse(data=current_user, isSuccess=True, message="Current user retrieved successfully.")

@router.get("/{user_id}", response_model=ApiResponse[user_schema.User], dependencies=[Depends(get_current_user)])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_profile(db, user_id=user_id)
    if db_user is None:
        raise EntityNotFoundException(entity_name="User", entity_id=user_id)
    return ApiResponse(data=db_user, isSuccess=True, message="User profile retrieved.")

@router.put("/{user_id}", response_model=ApiResponse[user_schema.User], dependencies=[Depends(get_current_user)])
def update_user(user_id: int, user: user_schema.UserUpdate, db: Session = Depends(get_db)):
    db_user = user_service.update_existing_user(db, user_id=user_id, user_update=user)
    if db_user is None:
        raise EntityNotFoundException(entity_name="User", entity_id=user_id)
    return ApiResponse(data=db_user, isSuccess=True, message="User updated successfully.")

@router.delete("/{user_id}", dependencies=[Depends(get_current_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = user_service.remove_user(db, user_id=user_id)
    if not success:
        raise EntityNotFoundException(entity_name="User", entity_id=user_id)
    return ApiResponse(data=None, isSuccess=True, message="User deleted successfully.")
