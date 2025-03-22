import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
from datetime import datetime

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file if it exists
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed. Using environment variables directly.")

# Initialize the FastAPI app
app = FastAPI(title="Gemini Chatbot API")

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the Gemini API
# You need to set your API key in an environment variable or configure it here
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    # For demo purposes, you can set it directly here (not recommended for production)
    # GOOGLE_API_KEY = "your-api-key"
    print("Warning: GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=GOOGLE_API_KEY)

# Setup the model - using only gemini-1.5-flash
MODEL_NAME = "gemini-1.5-flash"
try:
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"Using model: {MODEL_NAME}")
except Exception as e:
    print(f"Warning: Failed to initialize {MODEL_NAME}: {str(e)}")
    model = None

# Define model-related classes
class ModelInfo(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None

class ModelsResponse(BaseModel):
    available_models: List[ModelInfo]
    count: int = Field(..., description="Total number of available models")
    
    @field_validator('count', mode='before')
    @classmethod
    def set_count(cls, v, info):
        return len(info.data.get('available_models', []))

# Define message-related models
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    
    @field_validator('messages')
    @classmethod
    def messages_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError('At least one message is required')
        return v

class ChatResponse(BaseModel):
    response: str
    usage: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    model: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Check if we have a working model
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail=f"Model {MODEL_NAME} is not available. Please check your API key and permissions."
        )
            
    # Extract the user's most recent message
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # Format history for Gemini
    try:
        chat = model.start_chat(
            history=[
                {"role": msg.role.value, "parts": [msg.content]} 
                for msg in request.messages[:-1]  # All except the last message
            ]
        )
        
        # Get the last message to send
        last_message = request.messages[-1]
        
        # Generate response
        response = chat.send_message(last_message.content)
        
        # Create a usage object similar to OpenAI's format
        usage = {
            "prompt_tokens": len(" ".join([m.content for m in request.messages]).split()),
            "completion_tokens": len(response.text.split()),
            "total_tokens": len(" ".join([m.content for m in request.messages]).split()) + len(response.text.split())
        }
        
        return ChatResponse(response=response.text, usage=usage)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", model=MODEL_NAME)

# Endpoint to list available models
@app.get("/models", response_model=ModelsResponse)
async def list_models():
    try:
        models_list = genai.list_models()
        available_models = [
            ModelInfo(
                name=model.name, 
                display_name=model.display_name,
                description=getattr(model, 'description', None)
            ) 
            for model in models_list
        ]
        return ModelsResponse(available_models=available_models)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn backend:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True) 