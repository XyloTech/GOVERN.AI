"""
Training Data Collector for Xylotech Custom Models
Collects conversation data for fine-tuning
"""
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.chat import ChatMessage


def collect_training_data(output_file: str = "training_data.json", limit: int = 1000):
    """
    Collect training data from chat history
    
    Args:
        output_file: Output JSON file path
        limit: Maximum number of conversations to collect
    """
    db: Session = SessionLocal()
    
    try:
        # Get chat messages ordered by conversation
        messages = db.query(ChatMessage)\
            .order_by(ChatMessage.user_id, ChatMessage.created_at)\
            .limit(limit * 2)\
            .all()
        
        # Group messages by user and create conversation pairs
        training_data = []
        current_user = None
        current_query = None
        
        for message in messages:
            if message.role == "user":
                current_user = message.user_id
                current_query = message.content
            elif message.role == "assistant" and current_query:
                # Only include if assistant response is not an error
                metadata = message.message_metadata or {}
                if not metadata.get("error", False):
                    training_data.append({
                        "input": current_query,
                        "output": message.content,
                        "timestamp": message.created_at.isoformat() if message.created_at else None,
                        "user_id": current_user
                    })
                current_query = None
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Collected {len(training_data)} training examples")
        print(f"📁 Saved to: {output_file}")
        
        return training_data
    
    except Exception as e:
        print(f"❌ Error collecting training data: {e}")
        return []
    
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    output_file = sys.argv[1] if len(sys.argv) > 1 else "training_data.json"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    
    print(f"🔍 Collecting training data (limit: {limit})...")
    collect_training_data(output_file, limit)

