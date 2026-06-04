from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import user_repository
from app.schemas import user_schema

def register_user(db: Session, user: user_schema.UserCreate):
    # Here you can add logic like checking if email exists
    return user_repository.create_user(db, user)

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return user_repository.get_users(db, skip=skip, limit=limit)

def get_profile(db: Session, user_id: int):
    return user_repository.get_user(db, user_id)

def update_existing_user(db: Session, user_id: int, user_update: user_schema.UserUpdate):
    return user_repository.update_user(db, user_id, user_update)

def remove_user(db: Session, user_id: int):
    return user_repository.delete_user(db, user_id)