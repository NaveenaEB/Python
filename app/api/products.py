from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.schemas import product_schema
from app.services import product_service
from app.api.users import get_current_user
from app.core.database import get_db

router = APIRouter()

class ProductFilter(BaseModel):
    search_text: Optional[str] = None
    status: Optional[str] = None

@router.post("", response_model=product_schema.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: product_schema.ProductCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Ensure the product is linked to the currently authenticated user
    product.user_id = current_user.id
    return product_service.create_product(db=db, product=product)

@router.get("", response_model=List[product_schema.Product], dependencies=[Depends(get_current_user)])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product_service.get_all_products(db, skip=skip, limit=limit)

@router.post("/filter", response_model=List[product_schema.Product])
def filter_products(filters: ProductFilter, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # This endpoint allows filtering products by search text and status via POST body
    return product_service.filter_products(db, filters=filters)

@router.get("/{product_id}", response_model=product_schema.Product, dependencies=[Depends(get_current_user)])
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = product_service.get_product_by_id(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=product_schema.Product)
def update_product(product_id: int, product: product_schema.ProductUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_product = product_service.update_existing_product(db, product_id=product_id, product_update=product)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return db_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    success = product_service.remove_product(db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"message": "Product deleted successfully"}