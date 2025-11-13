"""
AI Copilot API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.services.copilot_service import CopilotService

router = APIRouter()


class CopilotQuery(BaseModel):
    query: str
    context: dict = {}  # Optional context like contract_id, report_id, etc.


@router.post("/query")
async def query_copilot(
    query_data: CopilotQuery,
    db: Session = Depends(get_db)
):
    """Query the AI Copilot with natural language"""
    copilot_service = CopilotService(db)
    response = await copilot_service.process_query(query_data.query, query_data.context)
    return {
        "query": query_data.query,
        "response": response,
        "sources": response.get("sources", []),
        "data": response.get("data", {})
    }


