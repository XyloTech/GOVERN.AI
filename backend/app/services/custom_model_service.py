"""
Custom Model Service for Xylotech GovernAI
Supports local models, fine-tuned models, and custom model architectures
"""
from typing import Optional, Dict, Any, List
import json
import time
from abc import ABC, abstractmethod


class BaseModelInterface(ABC):
    """Abstract base class for model interfaces"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from prompt"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if model is available"""
        pass


class OllamaModel(BaseModelInterface):
    """Local model using Ollama"""
    
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self._available = None
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        if self._available is None:
            try:
                import httpx
                with httpx.Client(timeout=2.0) as client:
                    response = client.get(f"{self.base_url}/api/tags")
                    self._available = response.status_code == 200
            except:
                self._available = False
        return self._available
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama"""
        import httpx
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    
    def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return [m.get("name", "") for m in models]
        except:
            pass
        return []


class HuggingFaceModel(BaseModelInterface):
    """Local model using Hugging Face Transformers"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load the model"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"[CustomModel] Loading HuggingFace model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            print(f"[CustomModel] Model loaded successfully")
        except Exception as e:
            print(f"[CustomModel] Failed to load model: {e}")
            self.model = None
            self.tokenizer = None
    
    def is_available(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.tokenizer is not None
    
    async def generate(self, prompt: str, max_length: int = 512, **kwargs) -> str:
        """Generate response using HuggingFace model"""
        if not self.is_available():
            return "Model not available. Please check model loading."
        
        try:
            import torch
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            if hasattr(self.model, 'generate'):
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=max_length,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        **kwargs
                    )
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Remove the prompt from response
                if response.startswith(prompt):
                    response = response[len(prompt):].strip()
                return response
            else:
                return "Model does not support generation."
        except Exception as e:
            print(f"[CustomModel] Generation error: {e}")
            return f"Error generating response: {str(e)}"


class FineTunedModel(BaseModelInterface):
    """Fine-tuned model wrapper"""
    
    def __init__(self, base_model: BaseModelInterface, fine_tune_data: Optional[List[Dict]] = None):
        self.base_model = base_model
        self.fine_tune_data = fine_tune_data or []
        self.fine_tuned = False
    
    def is_available(self) -> bool:
        """Check if base model is available"""
        return self.base_model.is_available()
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate with fine-tuned context"""
        # Add fine-tuning context to prompt if available
        enhanced_prompt = self._enhance_prompt(prompt)
        return await self.base_model.generate(enhanced_prompt, **kwargs)
    
    def _enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with fine-tuning examples"""
        if not self.fine_tune_data:
            return prompt
        
        # Add few-shot examples from fine-tuning data
        examples = "\n\n".join([
            f"Example {i+1}:\nQ: {ex.get('input', '')}\nA: {ex.get('output', '')}"
            for i, ex in enumerate(self.fine_tune_data[:3])  # Use top 3 examples
        ])
        
        return f"{examples}\n\nNow answer this:\n{prompt}"
    
    def add_training_data(self, input_text: str, output_text: str):
        """Add training data for fine-tuning"""
        self.fine_tune_data.append({
            "input": input_text,
            "output": output_text,
            "timestamp": time.time()
        })
    
    def save_training_data(self, filepath: str):
        """Save training data to file"""
        with open(filepath, 'w') as f:
            json.dump(self.fine_tune_data, f, indent=2)
    
    def load_training_data(self, filepath: str):
        """Load training data from file"""
        try:
            with open(filepath, 'r') as f:
                self.fine_tune_data = json.load(f)
        except FileNotFoundError:
            print(f"[FineTunedModel] Training data file not found: {filepath}")


class CustomModelService:
    """Main service for managing custom models"""
    
    def __init__(self, model_type: str = "ollama", model_name: str = "llama3", **kwargs):
        self.model_type = model_type
        self.model_name = model_name
        self.model: Optional[BaseModelInterface] = None
        self._initialize_model(**kwargs)
    
    def _initialize_model(self, **kwargs):
        """Initialize the appropriate model based on type"""
        try:
            if self.model_type.lower() == "ollama":
                self.model = OllamaModel(
                    model_name=self.model_name,
                    base_url=kwargs.get("base_url", "http://localhost:11434")
                )
            elif self.model_type.lower() == "huggingface":
                self.model = HuggingFaceModel(model_name=self.model_name)
            elif self.model_type.lower() == "finetuned":
                base_model_type = kwargs.get("base_model_type", "ollama")
                base_model_name = kwargs.get("base_model_name", "llama3")
                
                if base_model_type == "ollama":
                    base = OllamaModel(model_name=base_model_name)
                else:
                    base = HuggingFaceModel(model_name=base_model_name)
                
                self.model = FineTunedModel(base)
                
                # Load training data if provided
                training_data_path = kwargs.get("training_data_path")
                if training_data_path:
                    self.model.load_training_data(training_data_path)
            else:
                print(f"[CustomModel] Unknown model type: {self.model_type}")
                self.model = None
        except Exception as e:
            print(f"[CustomModel] Failed to initialize model: {e}")
            self.model = None
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using the custom model"""
        if not self.model or not self.model.is_available():
            return "Custom model is not available. Please check configuration."
        
        try:
            return await self.model.generate(prompt, **kwargs)
        except Exception as e:
            print(f"[CustomModel] Generation error: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if model is available"""
        return self.model is not None and self.model.is_available()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "type": self.model_type,
            "name": self.model_name,
            "available": self.is_available()
        }

