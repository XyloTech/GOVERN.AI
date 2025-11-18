"""Test what model is actually responding"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.copilot_service import CopilotService
from app.core.database import SessionLocal

async def test():
    print("🔍 Testing actual model response...\n")
    
    db = SessionLocal()
    copilot = CopilotService(db)
    
    print("Model Status:")
    if copilot.model_service:
        info = copilot.model_service.get_model_info()
        print(f"  ✅ Using: {info.get('type')} / {info.get('name')}")
        print(f"  Custom: {info.get('using_custom')}")
    elif copilot.model:
        print("  ⚠️ Using: Gemini (fallback)")
    else:
        print("  ❌ No model")
    
    print("\nTesting query: 'Who are you?'")
    result = await copilot.process_query("Who are you?")
    response = result.get('answer', '')
    
    print(f"\nResponse: {response[:300]}")
    
    if "google" in response.lower() or "gemini" in response.lower():
        print("\n❌ PROBLEM: Response mentions Google/Gemini!")
        print("   The local model is not being used properly.")
    else:
        print("\n✅ GOOD: No Google mention - using local model!")

if __name__ == "__main__":
    asyncio.run(test())

