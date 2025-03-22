import subprocess
import os
import sys
import time
import webbrowser
from threading import Thread

def run_backend():
    """Run the FastAPI backend server"""
    backend_port = "8000"  # Hardcoded backend port
    print(f"Starting backend server on port {backend_port}...")
    if os.name == 'nt':  # Windows
        subprocess.run(["uvicorn", "backend:app", "--reload", "--port", backend_port], check=True)
    else:  # Unix/Linux/MacOS
        subprocess.run(["uvicorn", "backend:app", "--reload", "--port", backend_port], check=True)

def run_frontend():
    """Run the Streamlit frontend"""
    frontend_port = "8500"  # Hardcoded frontend port
    print(f"Starting frontend server on port {frontend_port}...")
    if os.name == 'nt':  # Windows
        subprocess.run(["streamlit", "run", "frontend.py", "--server.port", frontend_port], check=True)
    else:  # Unix/Linux/MacOS
        subprocess.run(["streamlit", "run", "frontend.py", "--server.port", frontend_port], check=True)

def open_browser():
    """Open the browser after a short delay"""
    time.sleep(3)  # Wait for servers to start
    frontend_port = "8500"  # Hardcoded frontend port
    print("Opening browser...")
    webbrowser.open(f"http://localhost:{frontend_port}")  # Streamlit frontend

if __name__ == "__main__":
    # Check for environment variables
    if not os.environ.get("GOOGLE_API_KEY"):
        # Try to load from .env if python-dotenv is installed
        try:
            from dotenv import load_dotenv
            load_dotenv()
            if not os.environ.get("GOOGLE_API_KEY"):
                print("Warning: GOOGLE_API_KEY not found in environment or .env file.")
                print("The application may not work correctly.")
        except ImportError:
            print("Warning: GOOGLE_API_KEY not set in environment variables.")
            print("The application may not work correctly.")
    
    # Start browser opening thread
    browser_thread = Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start backend thread
    backend_thread = Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Run frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0) 