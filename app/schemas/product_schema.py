from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    Name: str
    price: float
    quantity: int

class ProductCreate(ProductBase):
    user_id: int

class ProductUpdate(BaseModel):
    Name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

class Product(ProductBase):
    id: int
    user_id: Optional[int] = None
    class Config:
        from_attributes = True