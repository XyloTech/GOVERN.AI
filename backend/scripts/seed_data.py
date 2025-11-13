"""
Seed initial data for development
"""
from app.core.database import SessionLocal
from app.models.compliance import ComplianceFramework
from app.models.report import ReportTemplate

def seed_data():
    """Seed initial compliance frameworks and report templates"""
    db = SessionLocal()
    
    try:
        # Seed Compliance Frameworks
        frameworks = [
            ComplianceFramework(
                name="GDPR",
                description="General Data Protection Regulation",
                version="2018",
                requirements={"data_protection": "required", "consent_management": "required"},
                applicable_regions=["EU", "EEA"]
            ),
            ComplianceFramework(
                name="ISO 27001",
                description="Information Security Management",
                version="2022",
                requirements={"security_controls": "required", "risk_assessment": "required"},
                applicable_regions=["Global"]
            ),
            ComplianceFramework(
                name="SOC 2",
                description="Service Organization Control 2",
                version="2017",
                requirements={"security": "required", "availability": "required"},
                applicable_regions=["Global"]
            ),
            ComplianceFramework(
                name="HIPAA",
                description="Health Insurance Portability and Accountability Act",
                version="1996",
                requirements={"patient_privacy": "required", "data_security": "required"},
                applicable_regions=["US"]
            ),
        ]
        
        for framework in frameworks:
            existing = db.query(ComplianceFramework).filter(ComplianceFramework.name == framework.name).first()
            if not existing:
                db.add(framework)
        
        # Seed Report Templates
        templates = [
            ReportTemplate(
                name="Financial Summary",
                description="Monthly financial summary report",
                report_type="financial",
                template_config={"sections": ["revenue", "expenses", "profit"]},
                is_default=True
            ),
            ReportTemplate(
                name="Compliance Status",
                description="Compliance status across all frameworks",
                report_type="compliance",
                template_config={"sections": ["frameworks", "alerts", "risks"]},
                is_default=True
            ),
            ReportTemplate(
                name="Contract Overview",
                description="Overview of all contracts",
                report_type="contract",
                template_config={"sections": ["active", "expiring", "risks"]},
                is_default=False
            ),
        ]
        
        for template in templates:
            existing = db.query(ReportTemplate).filter(ReportTemplate.name == template.name).first()
            if not existing:
                db.add(template)
        
        db.commit()
        print("Data seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()


