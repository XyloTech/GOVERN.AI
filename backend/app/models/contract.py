"""
Contract Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    PENDING_RENEWAL = "pending_renewal"


class ContractType(str, enum.Enum):
    SUPPLIER = "supplier"
    CUSTOMER = "customer"
    PARTNERSHIP = "partnership"
    EMPLOYMENT = "employment"
    NDAs = "nda"
    OTHER = "other"


class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    contract_number = Column(String, unique=True, index=True)
    type = Column(String(50), default="other")  # Using String to avoid enum lookup issues with existing data
    status = Column(String(50), default="draft")  # Using String to avoid enum lookup issues
    
    # Parties
    party_a = Column(String, nullable=False)
    party_b = Column(String, nullable=False)
    
    # Dates
    effective_date = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    renewal_date = Column(DateTime(timezone=True))
    
    # Financial
    contract_value = Column(Float)
    currency = Column(String, default="USD")
    
    # Document
    file_path = Column(String)
    file_name = Column(String)
    file_type = Column(String)
    
    # AI Extracted Data
    extracted_clauses = Column(JSON)  # Store extracted clauses as JSON
    risk_score = Column(Float, default=0.0)
    risk_factors = Column(JSON)  # List of risk factors
    
    # Metadata
    tags = Column(JSON)  # Array of tags
    notes = Column(Text)
    
    # Relationships
    clauses = relationship("ContractClause", back_populates="contract", cascade="all, delete-orphan")
    risks = relationship("ContractRisk", back_populates="contract", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))


class ContractClause(Base):
    __tablename__ = "contract_clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    clause_type = Column(String, nullable=False)  # obligation, renewal, penalty, etc.
    clause_text = Column(Text, nullable=False)
    extracted_data = Column(JSON)  # Structured data from AI extraction
    page_number = Column(Integer)
    confidence_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    contract = relationship("Contract", back_populates="clauses")


class ContractRisk(Base):
    __tablename__ = "contract_risks"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    risk_type = Column(String, nullable=False)  # financial, legal, compliance, operational
    severity = Column(String)  # low, medium, high, critical
    description = Column(Text)
    mitigation_recommendations = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    contract = relationship("Contract", back_populates="risks")

