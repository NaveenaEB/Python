from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import salary_schema
from app.repositories import salary_repository
from app.services import salary_service
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=salary_schema.Salary, status_code=status.HTTP_201_CREATED)
def create_salary(salary: salary_schema.SalaryCreate, db: Session = Depends(get_db)):
    return salary_service.create_employee_salary(db=db, salary=salary)

@router.get("/", response_model=List[salary_schema.Salary])
def read_salaries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return salary_repository.get_salaries(db, skip=skip, limit=limit)

@router.get("/{salary_id}", response_model=salary_schema.Salary)
def read_salary(salary_id: int, db: Session = Depends(get_db)):
    db_salary = salary_repository.get_salary(db, salary_id=salary_id)
    if db_salary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary record not found")
    return db_salary

@router.put("/{salary_id}", response_model=salary_schema.Salary)
def update_salary(salary_id: int, salary: salary_schema.SalaryUpdate, db: Session = Depends(get_db)):
    db_salary = salary_repository.update_salary(db, salary_id=salary_id, salary_update=salary)
    if db_salary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary record not found")
    return db_salary

@router.delete("/{salary_id}")
def delete_salary(salary_id: int, db: Session = Depends(get_db)):
    success = salary_repository.delete_salary(db, salary_id=salary_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary record not found")
    return {"message": "Salary record deleted successfully"}