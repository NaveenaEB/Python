from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.salary_model import Salary
from app.schemas import salary_schema

def get_salary(db: Session, salary_id: int) -> Optional[Salary]:
    return db.query(Salary).filter(Salary.id == salary_id).first()

def get_salaries(db: Session, skip: int = 0, limit: int = 100) -> List[Salary]:
    return db.query(Salary).offset(skip).limit(limit).all()

def create_salary(db: Session, salary: salary_schema.SalaryCreate) -> Salary:
    db_salary = Salary(**salary.model_dump())
    db.add(db_salary)
    db.commit()
    db.refresh(db_salary)
    return db_salary

def update_salary(db: Session, salary_id: int, salary_update: salary_schema.SalaryUpdate) -> Optional[Salary]:
    db_salary = get_salary(db, salary_id)
    if db_salary:
        update_data = salary_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_salary, key, value)
        db.commit()
        db.refresh(db_salary)
    return db_salary

def delete_salary(db: Session, salary_id: int) -> bool:
    db_salary = get_salary(db, salary_id)
    if db_salary:
        db.delete(db_salary)
        db.commit()
        return True
    return False