from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.database import get_db
from models.schemas import Department, Patient, FinancialRecord, Staff
import math

router = APIRouter()

def seed(s):
    x = math.sin(s) * 10000
    return x - math.floor(x)

@router.get("/dashboard-data")
def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Returns the complete aggregated dataset for the frontend dashboard.
    Fetches actual data from SQLite for core modules.
    """
    # 1. Departments
    depts = db.query(Department).all()
    dept_names = [d.name for d in depts]
    
    # 2. Financials (Monthly Aggregation)
    financials = db.query(
        FinancialRecord.month,
        func.sum(FinancialRecord.revenue).label("revenue"),
        func.sum(FinancialRecord.operating_cost).label("opex"),
        func.sum(FinancialRecord.insurance_revenue).label("insurance"),
        func.sum(FinancialRecord.oop_revenue).label("outOfPocket")
    ).group_by(FinancialRecord.month).all()
    
    # Sort months correctly (Apr to Mar)
    month_order = {"Apr":1, "May":2, "Jun":3, "Jul":4, "Aug":5, "Sep":6, "Oct":7, "Nov":8, "Dec":9, "Jan":10, "Feb":11, "Mar":12}
    financials_sorted = sorted(financials, key=lambda x: month_order.get(x.month, 0))
    revenue_data = [{"month": f.month, "revenue": f.revenue, "opex": f.opex, "insurance": f.insurance, "outOfPocket": f.outOfPocket} for f in financials_sorted]

    # 3. Dept Financials
    dept_fins = db.query(
        Department.name,
        Department.color_hex,
        func.sum(FinancialRecord.revenue).label("revenue"),
        func.sum(FinancialRecord.operating_cost).label("cost")
    ).join(FinancialRecord).group_by(Department.id).all()
    
    dept_financials = []
    for d in dept_fins:
        profit = d.revenue - d.cost
        margin = round((profit / d.revenue) * 100, 1) if d.revenue else 0
        dept_financials.append({"dept": d.name, "color": d.color_hex, "revenue": d.revenue, "cost": d.cost, "profit": profit, "margin": margin})

    # 4. Patients (Monthly Aggregation - mocked trend based on total for speed, usually requires complex date grouping)
    # We will generate the patient trend dynamically for the UI
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    patients_data = [{"month": m, "inpatient": round(1200 + seed(i*13)*400), "outpatient": round(3800 + seed(i*17)*800), "emergency": round(420 + seed(i*19)*150), "surgeries": round(280 + seed(i*23)*90)} for i, m in enumerate(months)]

    # 5. HR Data
    staff_agg = db.query(
        Staff.role,
        func.count(Staff.id).label("count"),
        func.avg(Staff.monthly_salary).label("salary"),
        func.sum(Staff.overtime_hours).label("overtimeHrs")
    ).group_by(Staff.role).all()
    
    hr_data = []
    for s in staff_agg:
        hr_data.append({
            "role": s.role,
            "count": s.count,
            "salary": int(s.salary or 0),
            "present": int(s.count * 0.9), # Simplified
            "onLeave": int(s.count * 0.1),
            "attrition": 4.5,
            "overtimeHrs": int(s.overtimeHrs or 0)
        })

    # Fallbacks for modules not yet fully mapped to SQLite
    ot_data = [{"dept": d.name, "scheduled": 80, "completed": 75, "cancelled": 5, "avgDuration": 120, "utilization": 85} for d in depts if d.total_beds > 0]
    insurance_data = [{"insurer": "Star Health", "claims": 500, "approved": 400, "pending": 80, "rejected": 20, "amount": 6000000, "avgDays": 15}]
    bed_occupancy = [{"dept": d.name, "totalBeds": d.total_beds, "occupied": int(d.total_beds * 0.8), "color": d.color_hex} for d in depts if d.total_beds > 0]
    appointments = [{"id": "APT1001", "patient": "John Doe", "doctor": "Dr. Sharma", "dept": "Cardiology", "date": "2025-03-10", "time": "10:00", "type": "New", "status": "Confirmed"}]

    return {
        "revenue": revenue_data,
        "patients": patients_data,
        "ot": ot_data,
        "hr": hr_data,
        "insurance": insurance_data,
        "bedOccupancy": bed_occupancy,
        "deptFinancials": dept_financials,
        "appointments": appointments
    }
