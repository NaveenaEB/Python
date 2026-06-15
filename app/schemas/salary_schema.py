from pydantic import BaseModel
from typing import Optional

class SalaryBase(BaseModel):
    amount: float
    month: str
    year: int
    employee_id: Optional[int] = None

class SalaryCreate(SalaryBase):
    pass

class SalaryUpdate(BaseModel):
    amount: Optional[float] = None
    month: Optional[str] = None
    year: Optional[int] = None
    employee_id: Optional[int] = None

class Salary(SalaryBase):
    id: int
    class Config:
        from_attributes = True