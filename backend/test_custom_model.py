"""Test script to verify custom model is working"""
import asyncio
from app.services.xylotech_model_service import XylotechModelService
from app.services.copilot_service import CopilotService
from app.core.database import SessionLocal

async def test():
    print("🔍 Testing Custom Model Setup...\n")
    
    # Test Xylotech Model Service
    print("1. Testing XylotechModelService...")
    service = XylotechModelService()
    info = service.get_model_info()
    print(f"   Model Type: {info.get('type')}")
    print(f"   Model Name: {info.get('name')}")
    print(f"   Using Custom: {info.get('using_custom')}")
    print(f"   Available: {info.get('available')}")
    
    if service.is_available():
        print("\n2. Testing generation...")
        response = await service.generate("Say hello in a fun way!")
        print(f"   Response: {response[:100]}...")
        print("   ✅ Generation successful!")
    else:
        print("   ⚠️ Model not available")
    
    # Test Copilot Service
    print("\n3. Testing CopilotService...")
    db = SessionLocal()
    copilot = CopilotService(db)
    if copilot.model_service:
        print(f"   ✅ Using Custom Model: {copilot.model_service.get_model_info()}")
    elif copilot.model:
        print("   ⚠️ Using Gemini (custom model not available)")
    else:
        print("   ❌ No model available")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test())

