from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import user_repository
from app.schemas import user_schema
from app.core import security

def register_user(db: Session, user: user_schema.UserCreate):
    # Check if user already exists
    db_user = user_repository.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = security.get_password_hash(user.password)
    return user_repository.create_user(db, user, hashed_password)

def authenticate_user(db: Session, email: str, password: str):
    user = user_repository.get_user_by_email(db, email=email)
    if not user or not security.verify_password(password, user.hashed_password):
        return None
    return user

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return user_repository.get_users(db, skip=skip, limit=limit)

def get_profile(db: Session, user_id: int):
    return user_repository.get_user(db, user_id)

def update_existing_user(db: Session, user_id: int, user_update: user_schema.UserUpdate):
    return user_repository.update_user(db, user_id, user_update)

def remove_user(db: Session, user_id: int):
    return user_repository.delete_user(db, user_id)