from pydantic import BaseModel, Field
from typing import Optional

class SalaryBase(BaseModel):
    amount: float
    month: str
    year: int
    employee_id: Optional[int] = None

class SalaryCreate(BaseModel):
    amount: float = Field(gt=0)
    month: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1900)
    employee_id: int = Field(gt=0)

class SalaryUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    month: Optional[str] = Field(default=None, min_length=1, max_length=50)
    year: Optional[int] = Field(default=None, ge=1900)
    employee_id: Optional[int] = Field(default=None, gt=0)

class Salary(SalaryBase):
    id: int
    class Config:
        from_attributes = True
