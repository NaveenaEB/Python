import json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.features.users import repository as user_repository
from app.features.users import schema as user_schema
from app.core import security
from app.core.redis import redis_client

USER_CACHE_EXPIRY = 3600  # 1 hour

def invalidate_user_cache(user_id: int = None):
    """Helper to clear user-related cache keys."""
    redis_client.delete_pattern("users:list:*")
    if user_id:
        redis_client.delete(f"user:profile:{user_id}")

def register_user(db: Session, user: user_schema.UserCreate):
    # Check if user already exists
    db_user = user_repository.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = security.get_password_hash(user.password)
    new_user = user_repository.create_user(db, user, hashed_password)
    invalidate_user_cache()
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    user = user_repository.get_user_by_email(db, email=email)
    if not user or not security.verify_password(password, user.hashed_password):
        return None
    return user

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    cache_key = f"users:list:{skip}:{limit}"
    cached_users = redis_client.get(cache_key)
    
    if cached_users:
        return json.loads(cached_users)
        
    users = user_repository.get_users(db, skip=skip, limit=limit)
    # Convert SQLAlchemy models to dicts for JSON serialization
    user_list = [user_schema.User.model_validate(u).model_dump() for u in users]
    redis_client.setex(cache_key, USER_CACHE_EXPIRY, json.dumps(user_list))
    return users

def get_profile(db: Session, user_id: int):
    cache_key = f"user:profile:{user_id}"
    cached_user = redis_client.get(cache_key)
    
    if cached_user:
        return json.loads(cached_user)
        
    user = user_repository.get_user(db, user_id)
    if user:
        user_data = user_schema.User.model_validate(user).model_dump()
        redis_client.setex(cache_key, USER_CACHE_EXPIRY, json.dumps(user_data))
    return user

def update_existing_user(db: Session, user_id: int, user_update: user_schema.UserUpdate):
    updated_user = user_repository.update_user(db, user_id, user_update)
    invalidate_user_cache(user_id)
    return updated_user

def remove_user(db: Session, user_id: int):
    success = user_repository.delete_user(db, user_id)
    if success:
        invalidate_user_cache(user_id)
    return success
