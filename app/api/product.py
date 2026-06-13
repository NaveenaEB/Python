from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import product_schema
from app.repositories import product_repository
from app.services import product_service
from app.api.users import get_current_user
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=product_schema.product, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create_product(product: product_schema.productCreate, db: Session = Depends(get_db)):
    return product_service.create_employee_product(db=db, product=product)

@router.get("/", response_model=List[product_schema.product], dependencies=[Depends(get_current_user)])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product_service.get_all_products(db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=product_schema.product, dependencies=[Depends(get_current_user)])
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = product_service.get_product_by_id(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product record not found")
    return db_product

@router.put("/{product_id}", response_model=product_schema.product, dependencies=[Depends(get_current_user)])
def update_product(product_id: int, product: product_schema.productUpdate, db: Session = Depends(get_db)):
    db_product = product_service.update_existing_product(db, product_id=product_id, product_update=product)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product record not found")
    return db_product

@router.delete("/{product_id}", dependencies=[Depends(get_current_user)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    success = product_service.remove_product(db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product record not found")
    return {"message": "product record deleted successfully"}