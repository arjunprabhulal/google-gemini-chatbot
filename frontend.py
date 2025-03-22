import streamlit as st
import requests
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file if it exists
except ImportError:
    pass  # Silently continue if python-dotenv is not installed

# Configure the page
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="💬",
    layout="centered"
)

# Define shared Pydantic models to keep in sync with backend
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

# Constants
API_URL = "http://localhost:8000/chat"  # The FastAPI endpoint
API_HEALTH_URL = "http://localhost:8000/health"  # Health check endpoint

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "token_usage" not in st.session_state:
    st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

# Custom CSS to improve the appearance
st.markdown("""
<style>
.chat-message {
    padding: 1.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem; 
    display: flex;
    flex-direction: column;
}
.chat-message.user {
    background-color: #2b313e;
    border-bottom-right-radius: 0;
}
.chat-message.assistant {
    background-color: #475063;
    border-bottom-left-radius: 0;
}
.chat-message .message-content {
    display: flex;
    margin-bottom: 0;
}
</style>
""", unsafe_allow_html=True)

# Helper function to send messages to the API
def send_message(messages: List[Dict[str, str]]):
    try:
        # Convert to Pydantic models for validation
        formatted_messages = [
            ChatMessage(
                role=msg["role"],
                content=msg["content"]
            ) for msg in messages
        ]
        
        # Create request body
        request = ChatRequest(
            messages=formatted_messages
        )
        
        # Send request
        response = requests.post(
            API_URL,
            json=request.model_dump(exclude_none=True),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Update token usage if available
            if "usage" in data and data["usage"]:
                st.session_state.token_usage = data["usage"]
            return data["response"]
        else:
            st.error(f"Error from API: {response.status_code}, {response.text}")
            return "Sorry, I encountered an error while processing your request."
    except Exception as e:
        st.error(f"Failed to communicate with the API: {str(e)}")
        return "Sorry, I couldn't connect to the backend service."

# Check backend health
def check_health():
    try:
        response = requests.get(API_HEALTH_URL)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Display the chat title
st.title("💬 Gemini Chatbot")
st.subheader("Ask me anything!")

# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt
    })
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Show a spinner while waiting for response
        with st.spinner("Thinking..."):
            # Send the entire conversation history to maintain context
            response = send_message(st.session_state.messages)
        
        # Add assistant response to chat history
        message_placeholder.markdown(response)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response
        })

# Sidebar with configuration and info
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>📊 LLM Metrics</h2>", unsafe_allow_html=True)
    
    # Add styled divider
    st.markdown("<hr style='margin: 15px 0; border: 0; height: 1px; background: #4B5563;'>", unsafe_allow_html=True)
    
    # Add a clear button with custom styling
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display token usage with visual elements
    st.markdown("<h3 style='margin-top: 20px;'>🔤 Token Usage</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Prompt**")
        st.markdown(f"<div style='text-align: center; background: #364153; padding: 10px; border-radius: 5px;'>{st.session_state.token_usage.get('prompt_tokens', 0)}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("**Completion**")
        st.markdown(f"<div style='text-align: center; background: #364153; padding: 10px; border-radius: 5px;'>{st.session_state.token_usage.get('completion_tokens', 0)}</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
    st.markdown("**Total Tokens**")
    progress_pct = min(100, int(st.session_state.token_usage.get('total_tokens', 0) / 100))  # Scale for visual
    st.progress(progress_pct/100)
    st.markdown(f"<div style='text-align: center; font-weight: bold;'>{st.session_state.token_usage.get('total_tokens', 0)}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Check backend health
    health_info = check_health()
    if health_info:
        st.markdown("<hr style='margin: 20px 0; border: 0; height: 1px; background: #4B5563;'>", unsafe_allow_html=True)
        st.markdown("<h3>🖥️ System Status</h3>", unsafe_allow_html=True)
        
        # Create a nice status indicator
        status = health_info.get('status', 'Unknown')
        status_color = "#4CAF50" if status == "healthy" else "#F44336"
        
        st.markdown(f"""
        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
            <div style='width: 12px; height: 12px; background: {status_color}; border-radius: 50%; margin-right: 8px;'></div>
            <div><strong>Status:</strong> {status.capitalize()}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Model info with icon
        st.markdown(f"""
        <div style='margin: 10px 0;'>
            <div style='margin-bottom: 5px;'><strong>🤖 Model:</strong></div>
            <div style='background: #364153; padding: 8px; border-radius: 5px;'>{health_info.get('model', 'Unknown')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Version
        st.markdown(f"<div><strong>📦 Version:</strong> {health_info.get('version', 'Unknown')}</div>", unsafe_allow_html=True)
    else:
        st.error("⚠️ Backend is not available") 