"""
API v1 Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import contracts, compliance, reports, documents, copilot

api_router = APIRouter()

api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])


