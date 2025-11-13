"""
Compliance Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    AT_RISK = "at_risk"
    PENDING_REVIEW = "pending_review"


class ComplianceFramework(Base):
    __tablename__ = "compliance_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # GDPR, ISO27001, SOC2, etc.
    description = Column(Text)
    version = Column(String)
    requirements = Column(JSON)  # Structured requirements
    applicable_regions = Column(JSON)  # Array of regions/countries
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id"), nullable=False)
    status = Column(Enum(ComplianceStatus), default=ComplianceStatus.PENDING_REVIEW)
    
    # Compliance Details
    requirement_id = Column(String)  # Reference to specific requirement in framework
    requirement_description = Column(Text)
    evidence = Column(JSON)  # Links to documents, contracts, etc.
    
    # Assessment
    compliance_score = Column(Integer)  # 0-100
    last_assessed = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    
    # Related Entities
    related_contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    related_department = Column(String)
    
    # Metadata
    notes = Column(Text)
    assessed_by = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    framework = relationship("ComplianceFramework")


class ComplianceAlert(Base):
    __tablename__ = "compliance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    compliance_record_id = Column(Integer, ForeignKey("compliance_records.id"), nullable=False)
    alert_type = Column(String)  # deadline, violation, risk, update
    severity = Column(String)  # low, medium, high, critical
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    compliance_record = relationship("ComplianceRecord")


