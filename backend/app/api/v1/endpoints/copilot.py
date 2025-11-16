"""
AI Copilot API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.chat import ChatMessage
from app.services.copilot_service import CopilotService

router = APIRouter()


class CopilotQuery(BaseModel):
    query: str
    context: dict = {}  # Optional context like contract_id, report_id, etc.


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: str


@router.post("/query")
async def query_copilot(
    query_data: CopilotQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Query the AI Copilot with natural language and save to chat history"""
    print(f"[Copilot Endpoint] Received query from user {current_user.id}: {query_data.query[:50]}...")
    try:
        # Save user message
        try:
            user_message = ChatMessage(
                user_id=current_user.id,
                role="user",
                content=query_data.query,
                message_metadata=query_data.context if query_data.context else None
            )
            db.add(user_message)
            db.flush()
            print(f"[Copilot Endpoint] User message saved: ID {user_message.id}")
        except Exception as db_error:
            print(f"[Copilot Endpoint] Error saving user message: {db_error}")
            import traceback
            traceback.print_exc()
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save user message: {str(db_error)}"
            )
        
        # Process query
        try:
            print(f"[Copilot Endpoint] Creating CopilotService...")
            copilot_service = CopilotService(db)
            print(f"[Copilot Endpoint] Processing query...")
            response = await copilot_service.process_query(query_data.query, query_data.context or {})
            print(f"[Copilot Endpoint] Query processed, response received")
        except Exception as ai_error:
            print(f"[Copilot Endpoint] Error processing query: {ai_error}")
            import traceback
            traceback.print_exc()
            # Still try to save an error message
            try:
                error_message = ChatMessage(
                    user_id=current_user.id,
                    role="assistant",
                    content=f"I encountered an error processing your query: {str(ai_error)[:200]}. Please try again.",
                    message_metadata={"error": True, "error_type": type(ai_error).__name__}
                )
                db.add(error_message)
                db.commit()
            except:
                db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error processing query: {str(ai_error)[:200]}"
            )
        
        # Ensure we have a valid response
        if not response:
            print("[Copilot Endpoint] WARNING: Empty response from service")
            response = {
                "answer": "I apologize, but I'm having trouble processing your query right now. Please try again.",
                "sources": [],
                "data": {}
            }
        elif not response.get("answer"):
            print("[Copilot Endpoint] WARNING: Response missing 'answer' field")
            response["answer"] = "I apologize, but I couldn't generate a response. Please try again."
        
        # Save assistant response
        try:
            assistant_message = ChatMessage(
                user_id=current_user.id,
                role="assistant",
                content=response.get("answer", ""),
                message_metadata={
                    "sources": response.get("sources", []),
                    "data": response.get("data", {})
                } if response.get("sources") or response.get("data") else None
            )
            db.add(assistant_message)
            db.commit()
            print(f"[Copilot Endpoint] Assistant message saved: ID {assistant_message.id}")
        except Exception as db_error:
            print(f"[Copilot Endpoint] Error saving assistant message: {db_error}")
            import traceback
            traceback.print_exc()
            db.rollback()
            # Don't fail the request if we can't save the message, just log it
        
        return {
            "query": query_data.query,
            "response": response,
            "sources": response.get("sources", []),
            "data": response.get("data", {}),
            "message_id": assistant_message.id if 'assistant_message' in locals() else None
        }
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions as-is
        print(f"[Copilot Endpoint] HTTPException raised: {http_ex.status_code} - {http_ex.detail}")
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"❌ [Copilot Endpoint] Unexpected error ({error_type}): {error_msg}")
        print(f"[Copilot Endpoint] Full traceback:\n{error_trace}")
        
        # Rollback any pending transaction
        try:
            db.rollback()
            print("[Copilot Endpoint] Database rolled back")
        except Exception as rollback_error:
            print(f"[Copilot Endpoint] Error during rollback: {rollback_error}")
        
        # Save error message to chat (non-blocking)
        try:
            error_message = ChatMessage(
                user_id=current_user.id,
                role="assistant",
                content=f"I encountered an error: {error_msg[:200]}. Please try again or contact support.",
                message_metadata={"error": True, "error_type": error_type}
            )
            db.add(error_message)
            db.commit()
            print(f"[Copilot Endpoint] Error message saved to chat")
        except Exception as db_error:
            print(f"[Copilot Endpoint] Failed to save error message to chat: {db_error}")
            try:
                db.rollback()
            except:
                pass
        
        # Return more detailed error for debugging (but sanitize for security)
        error_detail = error_msg[:200] if len(error_msg) > 200 else error_msg
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query ({error_type}): {error_detail}. Check server logs for details."
        )


@router.get("/history")
async def get_chat_history(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for current user"""
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.user_id == current_user.id)\
        .order_by(ChatMessage.created_at.desc())\
        .limit(limit)\
        .all()
    
    # Reverse to get chronological order
    messages.reverse()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "metadata": msg.message_metadata,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]


@router.delete("/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear chat history for current user"""
    db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared"}


