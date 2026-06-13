from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import product_repository, salary_repository, user_repository
from app.schemas import product_schema

def create_product(db: Session, product: product_schema.ProductCreate):
    # Business Logic: Check if user exists before creating product
    user = user_repository.get_user(db, user_id=product.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {product.user_id} not found"
        )
    return product_repository.create_product(db, product)

def get_all_products(db: Session, skip: int = 0, limit: int = 100):
    return product_repository.get_products(db, skip=skip, limit=limit)

def get_product_by_id(db: Session, product_id: int):
    return product_repository.get_product(db, product_id=product_id)

def update_existing_product(db: Session, product_id: int, product_update: product_schema.ProductUpdate):
    return product_repository.update_product(db, product_id=product_id, product_update=product_update)

def remove_product(db: Session, product_id: int):
    return product_repository.delete_product(db, product_id=product_id)