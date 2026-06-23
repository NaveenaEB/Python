from sqlalchemy.orm import Session
from app.features.products import repository as product_repository
from app.features.users import repository as user_repository
from app.features.products.model import Product
from app.features.products import schema as product_schema
from app.common.exceptions.custom_exceptions import EntityNotFoundException

def create_product(db: Session, product: product_schema.ProductCreate):
    # Business Logic: Check if user exists before creating product
    user = user_repository.get_user(db, user_id=product.user_id)
    if not user:
        raise EntityNotFoundException(entity_name="User", entity_id=product.user_id)
    return product_repository.create_product(db, product)

def get_all_products(db: Session, skip: int = 0, limit: int = 100):
    return product_repository.get_products(db, skip=skip, limit=limit)

def get_product_by_id(db: Session, product_id: int):
    return product_repository.get_product(db, product_id=product_id)

def update_existing_product(db: Session, product_id: int, product_update: product_schema.ProductUpdate):
    return product_repository.update_product(db, product_id=product_id, product_update=product_update)

def remove_product(db: Session, product_id: int):
    return product_repository.delete_product(db, product_id=product_id)

def filter_products(db: Session, filters):
    query = db.query(Product)
    
    if filters.search_text:
        # Search by text in name or description (case-insensitive)
        search = f"%{filters.search_text}%"
        query = query.filter(Product.name.ilike(search) | Product.description.ilike(search))
        
    if filters.status:
        query = query.filter(Product.status == filters.status)
        
    return query.all()
