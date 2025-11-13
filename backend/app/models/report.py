"""
Report Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ReportType(str, enum.Enum):
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    CONTRACT = "contract"
    CUSTOM = "custom"


class ReportStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    report_type = Column(Enum(ReportType), nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT)
    
    # Content
    summary = Column(Text)  # AI-generated natural language summary
    data = Column(JSON)  # Structured report data
    visualizations = Column(JSON)  # Chart configurations
    
    # Metadata
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=True)
    
    # File
    file_path = Column(String)  # Generated PDF/Excel file path
    
    # Relationships
    kpis = relationship("KPI", back_populates="report", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    generated_by = Column(Integer, ForeignKey("users.id"))


class ReportTemplate(Base):
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    report_type = Column(Enum(ReportType), nullable=False)
    template_config = Column(JSON)  # Template structure and fields
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class KPI(Base):
    __tablename__ = "kpis"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    name = Column(String, nullable=False)
    value = Column(String)  # Can be number, percentage, etc.
    unit = Column(String)
    trend = Column(String)  # up, down, stable
    target = Column(String)
    status = Column(String)  # on_track, at_risk, off_track
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    report = relationship("Report", back_populates="kpis")

