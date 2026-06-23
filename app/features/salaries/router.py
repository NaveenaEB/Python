from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.features.salaries import schema as salary_schema
from app.common.schemas.api_response import ApiResponse
from app.features.salaries import service as salary_service
from app.common.exceptions.custom_exceptions import EntityNotFoundException
from app.features.users.router import get_current_user
from app.core.database import get_db

router = APIRouter()

@router.post("", response_model=ApiResponse[salary_schema.Salary], status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create_salary(salary: salary_schema.SalaryCreate, db: Session = Depends(get_db)):
    data = salary_service.create_employee_salary(db=db, salary=salary)
    return ApiResponse(data=data, isSuccess=True, message="Salary record created.")

@router.get("", response_model=ApiResponse[List[salary_schema.Salary]], dependencies=[Depends(get_current_user)])
def read_salaries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    salaries = salary_service.get_all_salaries(db, skip=skip, limit=limit)
    return ApiResponse(data=salaries, isSuccess=True, message="Salaries retrieved.")

@router.get("/{salary_id}", response_model=ApiResponse[salary_schema.Salary], dependencies=[Depends(get_current_user)])
def read_salary(salary_id: int, db: Session = Depends(get_db)):
    db_salary = salary_service.get_salary_by_id(db, salary_id=salary_id)
    if db_salary is None:
        raise EntityNotFoundException(entity_name="Salary record", entity_id=salary_id)
    return ApiResponse(data=db_salary, isSuccess=True, message="Salary record details.")

@router.put("/{salary_id}", response_model=ApiResponse[salary_schema.Salary], dependencies=[Depends(get_current_user)])
def update_salary(salary_id: int, salary: salary_schema.SalaryUpdate, db: Session = Depends(get_db)):
    db_salary = salary_service.update_existing_salary(db, salary_id=salary_id, salary_update=salary)
    if db_salary is None:
        raise EntityNotFoundException(entity_name="Salary record", entity_id=salary_id)
    return ApiResponse(data=db_salary, isSuccess=True, message="Salary record updated.")

@router.delete("/{salary_id}", dependencies=[Depends(get_current_user)])
def delete_salary(salary_id: int, db: Session = Depends(get_db)):
    success = salary_service.remove_salary(db, salary_id=salary_id)
    if not success:
        raise EntityNotFoundException(entity_name="Salary record", entity_id=salary_id)
    return ApiResponse(data=None, isSuccess=True, message="Salary record deleted successfully.")
