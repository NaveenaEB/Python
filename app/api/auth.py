from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import user_service
from app.core import security
from app.schemas import user_schema
from app.schemas.api_response import ApiResponse

router = APIRouter()

@router.post("/login", response_model=ApiResponse[user_schema.Token])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(subject=user.email)
    refresh_token = security.create_refresh_token(subject=user.email)
    return ApiResponse(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }, isSuccess=True, message="Login successful.")

@router.post("/refresh", response_model=ApiResponse[user_schema.Token])
def refresh_access_token(payload: user_schema.RefreshTokenRequest):
    token_data = security.verify_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    new_access_token = security.create_access_token(subject=token_data["sub"])
    return ApiResponse(data={
        "access_token": new_access_token,
        "refresh_token": payload.refresh_token,
        "token_type": "bearer"
    }, isSuccess=True, message="Token refreshed successfully.")