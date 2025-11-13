"""
Initialize database with tables
"""
from app.core.database import Base, engine
from app.models import (
    User, Contract, ContractClause, ContractRisk,
    ComplianceFramework, ComplianceRecord, ComplianceAlert,
    Report, ReportTemplate, KPI
)

def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()


