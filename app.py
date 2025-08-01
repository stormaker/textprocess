from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import concurrent.futures
from openai import OpenAI
import json
import time
import logging
import asyncio
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI(title="Text Processing Tool", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ConnectionTestRequest(BaseModel):
    api_key: str
    base_url: str = "https://api.openai.com/v1"

class ProcessTextRequest(BaseModel):
    text: str
    prompt: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    max_workers: int = 5
    session_id: Optional[str] = None

class ProcessingStatus(BaseModel):
    success: bool
    status: str
    progress: int
    total_chunks: int
    completed_chunks: int
    results: str = ""
    error: Optional[str] = None

# Simple text splitter implementation
class SimpleTextSplitter:
    def __init__(self, chunk_size=1100, chunk_overlap=20):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text):
        """Split text into chunks with overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If we're not at the end, try to find a good breaking point
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(start + self.chunk_size - 200, start)
                search_text = text[search_start:end]
                
                # Look for Chinese sentence endings
                for delimiter in ['。', '！', '？', '\n\n', '\n']:
                    last_pos = search_text.rfind(delimiter)
                    if last_pos != -1:
                        end = search_start + last_pos + len(delimiter)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks

class TextProcessor:
    def __init__(self):
        self.client = None
        self.processing_status = {}
    
    def initialize_client(self, api_key, base_url="https://api.openai.com/v1"):
        """Initialize OpenAI client with provided credentials"""
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            # Test the connection
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            return False
    
    def split_text(self, text, chunk_size=1100, chunk_overlap=20):
        """Split text into chunks using simple text splitter"""
        text_splitter = SimpleTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter.split_text(text)
    
    def process_chunk(self, chunk, index, prompt, model="gpt-4o"):
        """Process a single chunk of text"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "assistant",
                        "content": f"{prompt}：{chunk}"
                    }
                ],
                temperature=0,
                max_tokens=4000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error processing chunk {index}: {str(e)}")
            raise e
    
    def process_text_concurrently(self, text, prompt, model, session_id, max_workers=5):
        """Process text with concurrent execution and progress tracking"""
        try:
            # Initialize processing status
            self.processing_status[session_id] = {
                'status': 'splitting',
                'progress': 0,
                'total_chunks': 0,
                'completed_chunks': 0,
                'results': '',
                'error': None
            }
            
            # Split text into chunks
            chunks = self.split_text(text)
            total_chunks = len(chunks)
            
            self.processing_status[session_id].update({
                'status': 'processing',
                'total_chunks': total_chunks
            })
            
            logger.info(f"Processing {total_chunks} chunks for session {session_id}")
            
            results = [None] * total_chunks  # Pre-allocate results list
            
            # Process chunks in batches to avoid rate limiting
            batch_size = max_workers
            for i in range(0, total_chunks, batch_size):
                batch_chunks = chunks[i:i + batch_size]
                batch_indices = list(range(i, min(i + batch_size, total_chunks)))
                
                # Process batch concurrently
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {
                        executor.submit(self.process_chunk, chunk, idx, prompt, model): idx 
                        for idx, chunk in zip(batch_indices, batch_chunks)
                    }
                    
                    for future in concurrent.futures.as_completed(futures):
                        idx = futures[future]
                        try:
                            result = future.result()
                            results[idx] = result
                            
                            # Update progress
                            completed = sum(1 for r in results if r is not None)
                            self.processing_status[session_id].update({
                                'completed_chunks': completed,
                                'progress': int((completed / total_chunks) * 100)
                            })
                            
                        except Exception as e:
                            logger.error(f"Error in chunk {idx}: {str(e)}")
                            self.processing_status[session_id]['error'] = str(e)
                            raise e
                
                # Add delay between batches to avoid rate limiting
                if i + batch_size < total_chunks:
                    time.sleep(1)
            
            # Combine results
            final_result = '\n\n'.join(filter(None, results))
            
            self.processing_status[session_id].update({
                'status': 'completed',
                'progress': 100,
                'results': final_result
            })
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in concurrent processing: {str(e)}")
            self.processing_status[session_id].update({
                'status': 'error',
                'error': str(e)
            })
            raise e

# Initialize text processor
text_processor = TextProcessor()

# Serve static files
@app.get("/", response_class=HTMLResponse)
async def read_index():
    """Serve the main HTML file"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/styles.css")
async def get_styles():
    """Serve CSS file"""
    return FileResponse("styles.css", media_type="text/css")

@app.get("/script.js")
async def get_script():
    """Serve JavaScript file"""
    return FileResponse("script.js", media_type="application/javascript")

@app.post("/api/test-connection")
async def test_connection(request: ConnectionTestRequest):
    """Test OpenAI API connection"""
    try:
        if not request.api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        success = text_processor.initialize_client(request.api_key, request.base_url)
        
        if success:
            return {"success": True, "message": "Connection successful"}
        else:
            raise HTTPException(status_code=400, detail="Failed to connect to OpenAI API")
            
    except Exception as e:
        logger.error(f"Connection test error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-text")
async def process_text(request: ProcessTextRequest, background_tasks: BackgroundTasks):
    """Start text processing"""
    try:
        # Validation
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        if not request.api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Generate session ID if not provided
        session_id = request.session_id or str(int(time.time()))
        
        # Initialize client
        if not text_processor.initialize_client(request.api_key, request.base_url):
            raise HTTPException(status_code=400, detail="Failed to initialize OpenAI client")
        
        # Start processing in background with user-configured parallel workers
        max_workers = max(1, min(10, request.max_workers))  # Clamp between 1-10
        background_tasks.add_task(
            text_processor.process_text_concurrently,
            request.text,
            request.prompt,
            request.model,
            session_id,
            max_workers
        )
        
        return {
            "success": True, 
            "session_id": session_id,
            "message": "Processing started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process text error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/processing-status/{session_id}", response_model=ProcessingStatus)
async def get_processing_status(session_id: str):
    """Get processing status for a session"""
    try:
        status = text_processor.processing_status.get(session_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return ProcessingStatus(
            success=True,
            status=status['status'],
            progress=status['progress'],
            total_chunks=status['total_chunks'],
            completed_chunks=status['completed_chunks'],
            results=status.get('results', ''),
            error=status.get('error')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import fastapi
        import uvicorn
        import openai
        import pydantic
        import python_dotenv
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install required packages:")
        print("pip install fastapi uvicorn openai python-dotenv")
        exit(1)
    
    print("🚀 Starting Text Processing Server with FastAPI...")
    print("📝 Frontend available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔧 API endpoints:")
    print("   - POST /api/test-connection")
    print("   - POST /api/process-text") 
    print("   - GET /api/processing-status/{session_id}")
    print("   - GET /api/health")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)