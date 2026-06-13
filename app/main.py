from fastapi import FastAPI
from app.core.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, salaries, auth, products
# Import models to ensure they are registered with Base.metadata before create_all
from app.dbmodel import user_model, salary_model, product_model

# Create database tables
# In an enterprise app, you'd use Alembic migrations instead of this
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Enterprise User & Salary API",
    description="A modular FastAPI application",
    version="1.0.0"
)

# Configure CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000",  # Your React app's origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include routers from the routers module
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(salaries.router, prefix="/salaries", tags=["Salaries"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "user-salary-api"}