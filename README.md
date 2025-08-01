# Text Processing Tool (FastAPI Version)

A modern web-based text processing application that uses OpenAI's API to process and transform text content. Built with FastAPI backend and vanilla JavaScript frontend. This tool splits large texts into chunks and processes them concurrently for efficient handling.

## Features

- **Multi-line Text Input**: Large textarea with scrollbar support for texts over 20 lines
- **Custom Prompts**: Input dialog for processing instructions
- **Real-time Progress**: Progress bar showing processing status
- **Results Display**: Scrollable output area with download functionality
- **Settings Panel**: Configure OpenAI API key, base URL, model selection, and theme
- **Dark/Light Mode**: Toggle between themes
- **Concurrent Processing**: Efficient batch processing with rate limiting
- **FastAPI Backend**: Modern async Python web framework
- **Auto-generated API Docs**: Interactive API documentation at `/docs`

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration (Optional)

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. Run the Application

#### Option 1: Use the startup script (Recommended)
```bash
python start.py
```

#### Option 2: Run directly
```bash
python app.py
```

#### Option 3: Use uvicorn directly
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The application will start on `http://localhost:8000`

## Usage

1. **Open the application** in your web browser at `http://localhost:8000`

2. **Configure Settings**:
   - Click the ⚙️ Settings button
   - Enter your OpenAI API key
   - Configure base URL if using a different endpoint
   - Select your preferred model (GPT-4o, GPT-4, GPT-3.5 Turbo)
   - Toggle dark mode if desired
   - Click "Save Settings"

3. **Process Text**:
   - Paste your text in the input area
   - Modify the processing prompt if needed (default is optimized for meeting transcripts)
   - Click "Process Text"
   - Monitor the progress bar
   - Download results when processing is complete

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

- `GET /` - Serve the main application
- `GET /styles.css` - Serve CSS file
- `GET /script.js` - Serve JavaScript file
- `POST /api/test-connection` - Test OpenAI API connection
- `POST /api/process-text` - Start text processing
- `GET /api/processing-status/{session_id}` - Get processing status
- `GET /api/health` - Health check

## Default Processing Prompt

The application comes with a default prompt optimized for processing meeting transcripts:

```
你是会议记录整理人员，以下是一段录音的逐字稿，请逐字将其整理成前后连贯的文字，需要注意：
1.保留完整保留原始录音的所有细节。
2.尽量保留原文语义、语感。
3.请修改错别字，符合中文语法规范。
4.去掉说话人和时间戳。
5.采用第一人称：我。
6.请足够详细，字数越多越好。
7.保持原始录音逐字稿的语言风格。
```

## Technical Details

### Backend Architecture
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Background Tasks**: Asynchronous text processing
- **Concurrent Processing**: ThreadPoolExecutor for parallel chunk processing

### Text Chunking
- Custom text splitter implementation
- Default chunk size: 1100 characters
- Chunk overlap: 20 characters
- Smart sentence boundary detection for Chinese text

### Concurrent Processing
- Processes up to 3 chunks simultaneously
- Implements rate limiting with 1-second delays between batches
- Real-time progress tracking via session-based status endpoints

### Frontend Features
- Responsive design for desktop and mobile
- Local storage for settings persistence
- Error handling and user notifications
- File download functionality
- Theme switching (dark/light mode)

## File Structure

```
├── app.py              # FastAPI backend server
├── index.html          # Main HTML interface
├── styles.css          # CSS styling and themes
├── script.js           # Frontend JavaScript logic
├── requirements.txt    # Python dependencies
├── start.py            # Easy startup script
├── test_setup.py       # Setup verification script
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Development

### Running in Development Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reloading when code changes.

### Testing the Setup

```bash
python test_setup.py
```

This will verify that all dependencies are installed and the application is configured correctly.

## Troubleshooting

### Common Issues

1. **"Failed to connect to OpenAI API"**
   - Verify your API key is correct
   - Check if you have sufficient API credits
   - Ensure the base URL is correct

2. **"Processing failed"**
   - Check your internet connection
   - Verify the text input is not empty
   - Try reducing the text size if it's very large

3. **Slow processing**
   - Large texts take time to process
   - The application processes in batches to avoid rate limits
   - Consider breaking very large texts into smaller parts

4. **Port already in use**
   - Change the port in `app.py` or use: `uvicorn app:app --port 8001`

### Package Installation Issues

If you encounter issues installing packages:

```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Install packages individually
pip install fastapi uvicorn openai python-dotenv pydantic
```

## Advantages of FastAPI Version

- **Better Performance**: Async/await support for better concurrency
- **Auto Documentation**: Interactive API docs generated automatically
- **Type Safety**: Pydantic models for request/response validation
- **Modern Python**: Uses latest Python features and best practices
- **Better Error Handling**: Structured error responses with proper HTTP status codes
- **Scalability**: Built for production use with proper async handling

## License

This project is open source and available under the MIT License.