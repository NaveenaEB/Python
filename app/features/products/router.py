from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.features.products import schema as product_schema
from app.common.schemas.api_response import ApiResponse
from app.features.products import service as product_service
from app.features.users.router import get_current_user
from app.common.exceptions.custom_exceptions import EntityNotFoundException
from app.core.database import get_db

router = APIRouter()

class ProductFilter(BaseModel):
    search_text: Optional[str] = None
    status: Optional[str] = None

@router.post("", response_model=ApiResponse[product_schema.Product], status_code=status.HTTP_201_CREATED)
def create_product(product: product_schema.ProductCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Ensure the product is linked to the currently authenticated user
    product.user_id = current_user.id
    data = product_service.create_product(db=db, product=product)
    return ApiResponse(data=data, isSuccess=True, message="Product created successfully.")

@router.get("", response_model=ApiResponse[List[product_schema.Product]], dependencies=[Depends(get_current_user)])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = product_service.get_all_products(db, skip=skip, limit=limit)
    return ApiResponse(data=data, isSuccess=True, message="Products retrieved successfully.")

@router.post("/filter", response_model=ApiResponse[List[product_schema.Product]])
def filter_products(filters: ProductFilter, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # This endpoint allows filtering products by search text and status via POST body
    data = product_service.filter_products(db, filters=filters)
    return ApiResponse(data=data, isSuccess=True, message="Filtered list retrieved successfully.")

@router.get("/{product_id}", response_model=ApiResponse[product_schema.Product], dependencies=[Depends(get_current_user)])
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = product_service.get_product_by_id(db, product_id=product_id)
    if db_product is None:
        raise EntityNotFoundException(entity_name="Product", entity_id=product_id)
    return ApiResponse(data=db_product, isSuccess=True, message="Product details retrieved successfully.")

@router.put("/{product_id}", response_model=ApiResponse[product_schema.Product])
def update_product(product_id: int, product: product_schema.ProductUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_product = product_service.update_existing_product(db, product_id=product_id, product_update=product)
    if db_product is None:
        raise EntityNotFoundException(entity_name="Product", entity_id=product_id)
    return ApiResponse(data=db_product, isSuccess=True, message="Product updated successfully.")

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    success = product_service.remove_product(db, product_id=product_id)
    if not success:
        raise EntityNotFoundException(entity_name="Product", entity_id=product_id)
    return ApiResponse(data=None, isSuccess=True, message="Product deleted successfully.")
