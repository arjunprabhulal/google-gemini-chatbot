# Gemini Chatbot with FastAPI and Streamlit

A modern chatbot application using Google's Gemini models with a FastAPI backend and Streamlit frontend.

![Gemini Chatbot Screenshot](images/image.png)

## Features

- FastAPI backend with multiple Gemini model support (1.5 Flash, 1.5 Pro, 2.0 Flash-Lite, 2.0 Flash)
- Sleek Streamlit frontend with a modern, responsive UI
- Interactive model selection with different capabilities for various use cases
- Conversation history maintained during the session
- One-click conversation reset
- Token usage tracking with visual indicators
- System health monitoring and available models display
- Custom styling with dark mode theme
- Pydantic models for structured data validation

## Logs Visualization

The application provides detailed logging information during runtime:

![Application Logs](images/logs.png)

## Setup Instructions

### Prerequisites

- Python 3.8+
- Google API key for Gemini (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))
- A Google Cloud project with the Gemini API enabled (may require billing setup)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/arjunprabhulal/google-gemini-chatbot.git
cd google-gemini-chatbot
```

2. Create and activate a virtual environment:
```bash
# For macOS/Linux
python -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:

   Copy the example .env file and add your API key:
   ```bash
   cp .env.example .env
   # Edit the .env file with your Google Gemini API key
   ```

### Running the Application

Using the integrated run script (recommended):
```bash
python run_app.py
```

The application runs on hardcoded ports:
- Backend (FastAPI): http://localhost:8000
- Frontend (Streamlit): http://localhost:8500

To access the API documentation, visit:
- API Docs: http://localhost:8000/docs

### Using the Application

1. Open http://localhost:8500 in your browser
2. Select your preferred Gemini model from the sidebar dropdown:
   - Gemini 1.5 Flash: Balanced speed and capabilities (default)
   - Gemini 1.5 Pro: Advanced reasoning for complex tasks
   - Gemini 2.0 Flash-Lite: Efficient processing
   - Gemini 2.0 Flash: Latest capabilities with improved performance
3. Type your messages in the chat input
4. Monitor token usage and system status in the sidebar
5. Clear the conversation history when needed

## Project Structure

- `backend.py`: FastAPI server with Gemini API integration and model management
- `frontend.py`: Streamlit UI with model selection and chat interface
- `run_app.py`: Script to start both services
- `requirements.txt`: Python dependencies

## API Documentation

### Chat Endpoint

```
POST /chat
```

Request body:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "model": "gemini-1.5-pro"
}
```

Response:
```json
{
  "response": "I'm doing well, thank you for asking! How can I help you today?",
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 14,
    "total_tokens": 19
  },
  "created_at": "2023-05-01T12:00:00.000Z"
}
```

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model": "gemini-1.5-flash",
  "available_models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-lite", "gemini-2.0-flash"],
  "version": "1.0.0",
  "timestamp": "2023-05-01T12:00:00.000Z"
}
```

### List Models

```
GET /models
```

## Future Enhancements

Potential improvements for future versions:
- Multimodal support for image processing
- Chat history persistence across sessions
- User authentication and personalized conversations
- Fine-tuning options for specific use cases
- Advanced prompt engineering tools
- Response streaming for faster interactions

## License

MIT

## Acknowledgements

- Google Generative AI for the Gemini models
- FastAPI for the backend framework
- Streamlit for the frontend interface 