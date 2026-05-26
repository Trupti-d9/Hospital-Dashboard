import math
from datetime import date, timedelta
import random
from sqlalchemy.orm import Session
from models.database import engine, Base, SessionLocal
from models.schemas import Department, Patient, FinancialRecord, Staff
from models.graph_db import graph_db

print("Creating SQLite tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def seed(s):
    x = math.sin(s) * 10000
    return x - math.floor(x)

def seed_sqlite(db: Session):
    print("Seeding Departments...")
    depts = [
        {"name": "Cardiology", "head": "Dr. Ramesh Iyer", "beds": 60, "color": "#e74c3c"},
        {"name": "Orthopaedics", "head": "Dr. Meena Suresh", "beds": 50, "color": "#3498db"},
        {"name": "Neurology", "head": "Dr. Arjun Pillai", "beds": 45, "color": "#9b59b6"},
        {"name": "Oncology", "head": "Dr. Priya Nair", "beds": 55, "color": "#e67e22"},
        {"name": "Paediatrics", "head": "Dr. Kavitha Rajan", "beds": 40, "color": "#27ae60"},
        {"name": "Gynaecology", "head": "Dr. Sujatha Venkat", "beds": 35, "color": "#f39c12"},
        {"name": "Emergency", "head": "Dr. Karthik Mohan", "beds": 30, "color": "#e74c3c"},
        {"name": "ICU / Critical Care", "head": "Dr. Balaji Krishnan", "beds": 40, "color": "#c0392b"},
        {"name": "Radiology", "head": "Dr. Deepa Srinivasan", "beds": 0, "color": "#1abc9c"},
        {"name": "Pharmacy", "head": "Mr. Senthil Kumar", "beds": 0, "color": "#34495e"},
    ]
    
    dept_objs = []
    for d in depts:
        obj = Department(name=d["name"], head_doctor=d["head"], total_beds=d["beds"], color_hex=d["color"])
        db.add(obj)
        dept_objs.append(obj)
    db.commit()

    print("Seeding Patients...")
    insurances = ["Star Health", "HDFC ERGO", "Bajaj Allianz", "New India Assurance", "United India", "Medi Assist TPA"]
    types = ["inpatient", "outpatient", "emergency"]
    
    for i in range(1500):
        val = seed(i)
        dept_id = int(val * 100) % 10 + 1
        age = int(val * 80) + 1
        ins = insurances[int(val * 100) % len(insurances)]
        p_type = types[int(val * 100) % len(types)]
        
        admit_date = date(2025, 1, 1) + timedelta(days=int(val * 365))
        discharge_date = admit_date + timedelta(days=int(val * 10) + 1) if p_type == "inpatient" else admit_date
        
        p = Patient(
            name=f"Patient_{i}",
            age=age,
            gender="M" if val > 0.5 else "F",
            department_id=dept_id,
            admission_date=admit_date,
            discharge_date=discharge_date,
            type=p_type,
            diagnosis="Standard Diagnosis",
            insurance_provider=ins,
            bill_amount=val * 100000,
            status="Discharged" if discharge_date < date.today() else "Admitted"
        )
        db.add(p)
    db.commit()

    print("Seeding Financials...")
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    for m_idx, m in enumerate(months):
        for d_idx, d in enumerate(dept_objs):
            f = FinancialRecord(
                month=m,
                year=2024 if m_idx < 9 else 2025,
                department_id=d.id,
                revenue=round(800000 + seed(m_idx * 10 + d_idx) * 2200000),
                operating_cost=round(500000 + seed(m_idx * 13 + d_idx) * 1500000),
                insurance_revenue=round(320000 + seed(m_idx * 17 + d_idx) * 150000),
                oop_revenue=round(280000 + seed(m_idx * 19 + d_idx) * 100000)
            )
            db.add(f)
    db.commit()

    print("Seeding HR/Staff...")
    roles = [
        {"role": "Senior Consultant", "count": 45, "salary": 280000},
        {"role": "Junior Consultant", "count": 62, "salary": 180000},
        {"role": "Resident Doctor", "count": 88, "salary": 95000},
        {"role": "Staff Nurse", "count": 210, "salary": 42000},
        {"role": "Lab Technician", "count": 55, "salary": 35000},
    ]
    for r_idx, r in enumerate(roles):
        for i in range(r["count"]):
            val = seed(r_idx * 100 + i)
            s = Staff(
                name=f"Staff_{r_idx}_{i}",
                role=r["role"],
                department_id=int(val * 100) % 10 + 1,
                monthly_salary=r["salary"],
                join_date=date(2020, 1, 1) + timedelta(days=int(val * 1000)),
                status="active" if val > 0.05 else "leave",
                working_hours_per_week=40,
                overtime_hours=int(val * 20)
            )
            db.add(s)
    db.commit()

    print("SQLite Seeding Complete!")

def seed_neo4j():
    if not graph_db.driver:
        print("Neo4j driver not found. Skipping Neo4j seeding.")
        return

    print("Seeding Neo4j Graph Database...")
    graph_db.query("MATCH (n) DETACH DELETE n")

    graph_db.query('''
        UNWIND ['Cardiology', 'Orthopaedics', 'Neurology', 'Oncology', 'Paediatrics'] AS dept_name
        CREATE (d:Department {name: dept_name})
    ''')

    graph_db.query('''
        UNWIND range(1, 100) AS i
        MATCH (d:Department)
        WITH d, i ORDER BY rand() LIMIT 1
        CREATE (p:Patient {id: i, name: 'Patient_' + i, risk_score: rand() * 100})
        CREATE (p)-[:TREATED_IN]->(d)
    ''')
    print("Neo4j Seeding Complete!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_sqlite(db)
        seed_neo4j()
    finally:
        db.close()
