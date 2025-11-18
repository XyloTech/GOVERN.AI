"""
Xylotech Custom Model Service
Main service that integrates custom models with the GovernAI platform
"""
from typing import Optional, Dict, Any
from app.core.config import settings
from app.services.custom_model_service import CustomModelService
import google.generativeai as genai


class XylotechModelService:
    """
    Unified model service that can use either:
    - Custom Xylotech models (Ollama, HuggingFace, Fine-tuned)
    - Google Gemini (fallback)
    """
    
    def __init__(self):
        self.custom_model: Optional[CustomModelService] = None
        self.gemini_model = None
        self.use_custom = settings.USE_CUSTOM_MODEL
        
        # Initialize custom model if enabled
        if self.use_custom:
            try:
                self.custom_model = CustomModelService(
                    model_type=settings.CUSTOM_MODEL_TYPE,
                    model_name=settings.CUSTOM_MODEL_NAME,
                    base_url=settings.OLLAMA_BASE_URL,
                    training_data_path=settings.TRAINING_DATA_PATH
                )
                if self.custom_model.is_available():
                    print(f"[XylotechModel] Custom model initialized: {settings.CUSTOM_MODEL_TYPE}/{settings.CUSTOM_MODEL_NAME}")
                else:
                    print(f"[XylotechModel] Custom model not available, will use Gemini fallback")
                    self.use_custom = False
            except Exception as e:
                print(f"[XylotechModel] Failed to initialize custom model: {e}")
                self.use_custom = False
        
        # Initialize Gemini as fallback
        if not self.use_custom and settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                print(f"[XylotechModel] Using Gemini as primary model")
            except Exception as e:
                print(f"[XylotechModel] Failed to initialize Gemini: {e}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using custom model or Gemini fallback"""
        # Try custom model first if enabled
        if self.use_custom and self.custom_model and self.custom_model.is_available():
            try:
                response = await self.custom_model.generate(prompt, **kwargs)
                return response
            except Exception as e:
                print(f"[XylotechModel] Custom model error: {e}, falling back to Gemini")
        
        # Fallback to Gemini
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text if hasattr(response, 'text') else str(response)
            except Exception as e:
                print(f"[XylotechModel] Gemini error: {e}")
                return f"Error: Unable to generate response. {str(e)}"
        
        return "No model available. Please configure either custom model or Gemini API key."
    
    def is_available(self) -> bool:
        """Check if any model is available"""
        if self.use_custom and self.custom_model:
            return self.custom_model.is_available()
        return self.gemini_model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model configuration"""
        info = {
            "using_custom": self.use_custom,
            "available": self.is_available()
        }
        
        if self.use_custom and self.custom_model:
            info.update(self.custom_model.get_model_info())
        else:
            info["type"] = "gemini"
            info["name"] = "gemini-2.5-flash"
        
        return info

