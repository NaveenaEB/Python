from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import salary_repository, user_repository
from app.schemas import salary_schema

def create_employee_salary(db: Session, salary: salary_schema.SalaryCreate):
    # Business Logic: Check if employee exists before creating salary
    user = user_repository.get_user(db, user_id=salary.employee_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {salary.employee_id} not found"
        )
    return salary_repository.create_salary(db, salary)