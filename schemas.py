from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Time, Text
from sqlalchemy.orm import relationship
from .database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    head_doctor = Column(String(100))
    total_beds = Column(Integer)
    color_hex = Column(String(7))

    patients = relationship("Patient", back_populates="department")
    staff = relationship("Staff", back_populates="department")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))  # Should be masked in APIs for DPDP compliance
    age = Column(Integer)
    gender = Column(String(10))
    department_id = Column(Integer, ForeignKey("departments.id"))
    admission_date = Column(Date)
    discharge_date = Column(Date, nullable=True)
    type = Column(String(20)) # inpatient/outpatient/emergency
    diagnosis = Column(Text)
    insurance_provider = Column(String(100))
    bill_amount = Column(Float)
    status = Column(String(20))

    department = relationship("Department", back_populates="patients")

class FinancialRecord(Base):
    __tablename__ = "financials"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(10))
    year = Column(Integer)
    department_id = Column(Integer, ForeignKey("departments.id"))
    revenue = Column(Float)
    operating_cost = Column(Float)
    insurance_revenue = Column(Float)
    oop_revenue = Column(Float)

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    role = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"))
    monthly_salary = Column(Float)
    join_date = Column(Date)
    status = Column(String(20))
    working_hours_per_week = Column(Integer)
    overtime_hours = Column(Integer)

    department = relationship("Department", back_populates="staff")
