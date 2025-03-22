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
    model: str

# Constants
API_URL = "http://localhost:8000/chat"  # The FastAPI endpoint
API_HEALTH_URL = "http://localhost:8000/health"  # Health check endpoint

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "token_usage" not in st.session_state:
    st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-1.5-flash"

# Add custom CSS for sidebar styling
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

/* Sidebar styling */
section.main > div:nth-child(1) > div:nth-child(1) > div > div > div > div {
    background-color: #242934;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.sidebar-header {
    background: linear-gradient(90deg, #4a63a9, #3b4da6);
    margin: -10px -10px 15px -10px;
    padding: 20px 10px;
    border-radius: 10px 10px 0 0;
    text-align: center;
    color: white;
}
.sidebar-section {
    background-color: #2b313e;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
}
.sidebar-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 10px;
    border-bottom: 1px solid #3a4052;
    padding-bottom: 8px;
}
.model-box {
    background-color: #364153;
    border-radius: 8px;
    padding: 12px;
    margin-top: 10px;
    border-left: 4px solid #4a63a9;
}
.token-box {
    background-color: #364153;
    border-radius: 8px;
    text-align: center;
    padding: 10px;
}
.status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 8px;
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
            messages=formatted_messages,
            model=st.session_state.selected_model
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
    st.markdown('<div class="sidebar-header"><h1 style="font-size: 1.5rem; margin: 0;">🌟 Gemini AI</h1><p style="opacity: 0.8; margin: 5px 0 0 0;">Powered by Google LLM</p></div>', unsafe_allow_html=True)
    
    # Model selector section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🤖 Model Selection</div>', unsafe_allow_html=True)
    
    model_options = {
        "gemini-1.5-flash": "Gemini 1.5 Flash (Balanced)",
        "gemini-1.5-pro": "Gemini 1.5 Pro (Advanced)",
        "gemini-2.0-flash-lite": "Gemini 2.0 Flash-Lite (Efficient)",
        "gemini-2.0-flash": "Gemini 2.0 Flash (Latest)",
    }
    
    # Cleaner model selector with descriptions
    model_descriptions = {
        "gemini-1.5-flash": "Fast responses, good for general use",
        "gemini-1.5-pro": "Enhanced reasoning and complex tasks",
        "gemini-2.0-flash-lite": "Lightweight and efficient processing",
        "gemini-2.0-flash": "Latest capabilities with improved performance"
    }
    
    selected_model = st.selectbox(
        "Choose a model",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=list(model_options.keys()).index(st.session_state.selected_model)
    )
    
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.session_state.messages = []  # Clear chat when model changes
        st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        st.rerun()
    
    # Show description of currently selected model instead of redundant name
    if selected_model in model_descriptions:
        st.markdown(f'<div class="model-box"><small style="opacity: 0.8;">DESCRIPTION</small><br/><span>{model_descriptions[selected_model]}</span></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Conversation controls section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">💬 Conversation</div>', unsafe_allow_html=True)
    
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Token usage section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📊 Token Usage</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Input**")
        st.markdown(f'<div class="token-box">{st.session_state.token_usage.get("prompt_tokens", 0)}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("**Output**")
        st.markdown(f'<div class="token-box">{st.session_state.token_usage.get("completion_tokens", 0)}</div>', unsafe_allow_html=True)
    
    total_tokens = st.session_state.token_usage.get("total_tokens", 0)
    progress_pct = min(100, int(total_tokens / 100))  # Scale for visual
    st.markdown("<div style='margin-top: 12px;'><strong>Total Usage</strong></div>", unsafe_allow_html=True)
    st.progress(progress_pct/100)
    st.markdown(f'<div style="text-align: center; font-weight: bold; margin-top: 5px;">{total_tokens}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # System status section
    health_info = check_health()
    if health_info:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">⚙️ System Status</div>', unsafe_allow_html=True)
        
        # Status indicator
        status = health_info.get('status', 'Unknown')
        status_color = "#4CAF50" if status == "healthy" else "#F44336"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span class="status-dot" style="background-color: {status_color};"></span>
            <span><strong>Status:</strong> {status.capitalize()}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Available models in a scrollable area
        if 'available_models' in health_info and health_info['available_models']:
            st.markdown('<div style="margin: 10px 0;"><strong>Available Models</strong></div>', unsafe_allow_html=True)
            model_list = '<div style="max-height: 100px; overflow-y: auto; background-color: #313844; border-radius: 5px; padding: 8px; font-size: 0.9rem;">'
            for available_model in health_info['available_models']:
                model_list += f'<div style="margin: 3px 0;">• {available_model}</div>'
            model_list += '</div>'
            st.markdown(model_list, unsafe_allow_html=True)
        
        # Version info
        st.markdown(f'<div style="margin-top: 10px;"><strong>Version:</strong> {health_info.get("version", "Unknown")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-section" style="border-left: 4px solid #F44336;">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">⚙️ System Status</div>', unsafe_allow_html=True)
        st.markdown('<div style="color: #F44336;"><strong>⚠️ Backend is not available</strong></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) 