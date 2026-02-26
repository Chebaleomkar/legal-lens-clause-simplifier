from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import os
from dotenv import load_dotenv
import uvicorn
from contextlib import asynccontextmanager
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
BASE_MODEL_ID = "google/gemma-2b"
ADAPTER_MODEL_ID = "Agent-Omkar/legal-lens-clause-simplifier"
HF_TOKEN = os.environ.get("HF_TOKEN")

# Global variables for model and tokenizer
model = None
tokenizer = None
device = "cuda" if torch.cuda.is_available() else "cpu"

class SimplificationRequest(BaseModel):
    clause: str = Field(..., title="Legal Clause", description="The complicated legal clause to simplify")
    max_new_tokens: int = Field(default=256, title="Max New Tokens")
    temperature: float = Field(default=0.3, title="Temperature")

class SimplificationResponse(BaseModel):
    simplified_text: str

def format_prompt(clause: str) -> str:
    """Format the user input exactly like the training data."""
    return f"""<start_of_turn>user
Simplify the following legal clause into plain English:
{clause}
<end_of_turn>
<start_of_turn>model
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model and tokenizer on startup
    global model, tokenizer
    logger.info(f"Using device: {device}")
    
    if not HF_TOKEN:
        logger.warning("HF_TOKEN environment variable is not set. Gated models like Gemma might fail to download unless already cached.")

    try:
        logger.info(f"Loading base model: {BASE_MODEL_ID}")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, token=HF_TOKEN)
        
        # Load the base model (you can use quantization like bitsandbytes if you want, but sticking to standard for general compat)
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_ID,
            token=HF_TOKEN,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
            low_cpu_mem_usage=True
        )

        logger.info(f"Loading adapter: {ADAPTER_MODEL_ID}")
        model = PeftModel.from_pretrained(base_model, ADAPTER_MODEL_ID, token=HF_TOKEN)
        
        if device == "cpu":
            # Just move to CPU
            model.to("cpu")
            
        model.eval()
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        # Not exiting right away so app can at least start and report health error
    
    yield
    # Cleanup on shutdown
    model = None
    tokenizer = None

app = FastAPI(
    title="Legal Lens - Clause Simplifier API",
    description="API for simplifying complicated legal clauses into plain English using a fine-tuned Gemma-2b model.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    """Check if the model is loaded and ready."""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded or still loading.")
    return {"status": "healthy", "device": device}

@app.post("/simplify", response_model=SimplificationResponse)
async def simplify_clause(request: SimplificationRequest):
    """
    Takes a legal clause and returns a simplified version.
    """
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model is not available.")

    prompt = format_prompt(request.clause)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    try:
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            
        # Decode only the generated part
        input_length = inputs["input_ids"].shape[1]
        generated_tokens = outputs[0][input_length:]
        simplified_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        # Clean up model's extra output tags if any
        if "<end_of_turn>" in simplified_text:
            simplified_text = simplified_text.split("<end_of_turn>")[0].strip()

        return SimplificationResponse(simplified_text=simplified_text)
    
    except Exception as e:
        logger.error(f"Error during inference: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=True)
