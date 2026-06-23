from fastapi import FastAPI
from app.core.database import engine, Base
from app.features.users import router as users
from app.features.salaries import router as salaries
from app.features.auth import router as auth
from app.features.products import router as products
from app.common.exceptions.handlers import register_exception_handlers
from app.common.middleware.cors import CustomCORSMiddleware
# Import models to ensure they are registered with Base.metadata before create_all
from app.features.users import model as user_model
from app.features.salaries import model as salary_model
from app.features.products import model as product_model

# Create database tables
# In an enterprise app, you'd use Alembic migrations instead of this
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Enterprise User & Salary API",
    description="A modular FastAPI application",
    version="1.0.0"
)

# Register Custom Middleware
app.add_middleware(CustomCORSMiddleware)

# Include routers from the routers module
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(salaries.router, prefix="/salaries", tags=["Salaries"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Register centralized exception handlers
register_exception_handlers(app)

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "user-salary-api"}
