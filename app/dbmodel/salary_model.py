from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Salary(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    month = Column(String(50))
    year = Column(Integer)
    employee_id = Column(Integer, ForeignKey("users.id"))

    # Relationship with User model using string reference
    employee = relationship("User", back_populates="salaries")