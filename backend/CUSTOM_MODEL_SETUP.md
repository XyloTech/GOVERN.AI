# Custom Model Setup Guide - Xylotech GovernAI

This guide explains how to set up and use your own custom AI models with GovernAI.

## Overview

The custom model system supports:
- **Ollama** - Local models running via Ollama
- **HuggingFace** - Models from HuggingFace Hub
- **Fine-tuned Models** - Custom fine-tuned models with your data

## Option 1: Using Ollama (Recommended for Local Development)

### Installation

1. **Install Ollama:**
   ```bash
   # Windows (PowerShell)
   winget install Ollama.Ollama
   
   # Or download from: https://ollama.ai
   ```

2. **Start Ollama:**
   ```bash
   ollama serve
   ```

3. **Pull a model:**
   ```bash
   # Popular options:
   ollama pull llama3
   ollama pull mistral
   ollama pull codellama
   ollama pull phi
   ```

4. **Configure in `.env` or `config.py`:**
   ```python
   USE_CUSTOM_MODEL = True
   CUSTOM_MODEL_TYPE = "ollama"
   CUSTOM_MODEL_NAME = "llama3"  # or your chosen model
   OLLAMA_BASE_URL = "http://localhost:11434"
   ```

## Option 2: Using HuggingFace Models

### Installation

1. **Install dependencies:**
   ```bash
   pip install transformers torch accelerate
   ```

2. **Configure in `.env` or `config.py`:**
   ```python
   USE_CUSTOM_MODEL = True
   CUSTOM_MODEL_TYPE = "huggingface"
   CUSTOM_MODEL_NAME = "microsoft/DialoGPT-medium"  # or any HF model
   ```

### Recommended Models

- **Small & Fast:**
  - `microsoft/DialoGPT-small`
  - `gpt2`
  - `distilgpt2`

- **Medium:**
  - `microsoft/DialoGPT-medium`
  - `EleutherAI/gpt-neo-125M`

- **Large (requires more RAM/GPU):**
  - `microsoft/DialoGPT-large`
  - `EleutherAI/gpt-neo-1.3B`

## Option 3: Fine-tuning Your Own Model

### Step 1: Collect Training Data

Use the training data collector to gather conversations:

```python
from app.services.custom_model_service import FineTunedModel, OllamaModel

# Initialize fine-tuned model
base_model = OllamaModel("llama3")
fine_tuned = FineTunedModel(base_model)

# Add training examples
fine_tuned.add_training_data(
    input_text="What contracts do we have?",
    output_text="Here are the contracts in our system..."
)

# Save training data
fine_tuned.save_training_data("./training_data.json")
```

### Step 2: Fine-tune with Your Data

1. **Prepare training data** in JSON format:
   ```json
   [
     {
       "input": "User question",
       "output": "AI response",
       "timestamp": 1234567890
     }
   ]
   ```

2. **Configure fine-tuned model:**
   ```python
   USE_CUSTOM_MODEL = True
   CUSTOM_MODEL_TYPE = "finetuned"
   CUSTOM_MODEL_NAME = "llama3"  # base model
   TRAINING_DATA_PATH = "./training_data.json"
   ```

### Step 3: Advanced Fine-tuning (Optional)

For full fine-tuning, you'll need to use training scripts:

```bash
# Example using HuggingFace transformers
python scripts/fine_tune_model.py \
  --model_name microsoft/DialoGPT-medium \
  --train_data training_data.json \
  --output_dir ./models/xylotech-governai
```

## Configuration

### Environment Variables

Add to `.env` file:

```env
# Enable custom model
USE_CUSTOM_MODEL=True
CUSTOM_MODEL_TYPE=ollama
CUSTOM_MODEL_NAME=llama3
OLLAMA_BASE_URL=http://localhost:11434
TRAINING_DATA_PATH=./training_data.json
```

### Code Configuration

In `backend/app/core/config.py`:

```python
USE_CUSTOM_MODEL: bool = True
CUSTOM_MODEL_TYPE: str = "ollama"
CUSTOM_MODEL_NAME: str = "llama3"
```

## Testing Your Custom Model

1. **Check model availability:**
   ```python
   from app.services.xylotech_model_service import XylotechModelService
   
   service = XylotechModelService()
   print(service.get_model_info())
   print(f"Available: {service.is_available()}")
   ```

2. **Test generation:**
   ```python
   response = await service.generate("Hello, how are you?")
   print(response)
   ```

## Integration with Copilot

The copilot service automatically uses your custom model when `USE_CUSTOM_MODEL=True`. No code changes needed!

## Performance Tips

1. **Ollama:** Best for local development, easy setup
2. **HuggingFace:** More control, requires more resources
3. **Fine-tuning:** Best results but requires training data and compute

## Troubleshooting

### Ollama not found
- Make sure Ollama is installed and running
- Check `ollama serve` is running on port 11434
- Verify model is pulled: `ollama list`

### HuggingFace model too slow
- Use smaller models (DialoGPT-small instead of large)
- Enable GPU if available
- Use quantization: `torch_dtype=torch.float16`

### Out of memory
- Use smaller models
- Reduce batch size
- Use CPU instead of GPU for smaller models

## Next Steps

1. Choose your model type (Ollama recommended for start)
2. Install and configure
3. Test with simple queries
4. Collect training data from real usage
5. Fine-tune for better results

## Support

For issues or questions, contact Xylotech support.

