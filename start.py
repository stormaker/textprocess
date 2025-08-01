#!/usr/bin/env python3
"""
Simple startup script for the Text Processing Tool (FastAPI version)
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_packages():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import openai
        import pydantic
        import dotenv
        return True
    except ImportError:
        return False

def install_packages():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Text Processing Server with FastAPI...")
    print("📝 Frontend will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("⚙️  Configure your OpenAI API key in the settings panel")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8000')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the FastAPI app with uvicorn
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)

def main():
    """Main startup function"""
    print("🔧 Text Processing Tool - FastAPI Startup")
    print("=" * 45)
    
    # Check if packages are installed
    if not check_packages():
        print("❌ Required packages not found")
        print("🔄 Attempting to install packages...")
        
        if not install_packages():
            print("❌ Failed to install packages")
            print("Please manually run: pip install -r requirements.txt")
            return 1
        
        print("✅ Packages installed successfully")
    else:
        print("✅ All required packages found")
    
    # Start the server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    exit(main())