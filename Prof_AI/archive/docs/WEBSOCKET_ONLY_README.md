# ProfAI WebSocket Server - Simplified Setup

This project has been simplified to run **only the WebSocket server** on port 8765. All web server functionality (FastAPI/Flask on port 5001) has been removed.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file with your API keys:
```env
# Required for AI services
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
SARVAM_API_KEY=your_sarvam_key

# WebSocket server configuration (optional)
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8765
```

### 3. Start the WebSocket Server
```bash
python run_profai_websocket.py
```

The server will start on `ws://localhost:8765`

## 🧪 Testing the Connection

Run the included test script to verify everything is working:
```bash
python test_websocket_connection.py
```

## 📡 WebSocket API

### Connection
Connect to: `ws://localhost:8765`

### Message Types

#### 1. Ping/Pong (Connection Test)
```json
// Send
{"type": "ping", "message": "test"}

// Receive
{"type": "pong", "message": "Connection alive", "server_time": 1234567890}
```

#### 2. Chat with Audio
```json
// Send
{
    "type": "chat_with_audio",
    "message": "Your question here",
    "language": "en-IN",
    "request_id": "optional_id"
}

// Receive (multiple messages)
{"type": "processing_started", "message": "Generating response..."}
{"type": "text_response", "text": "AI response text"}
{"type": "audio_generation_started", "message": "Generating audio..."}
{"type": "audio_chunk", "chunk_id": 1, "audio_data": "base64_audio", "is_first_chunk": true}
{"type": "audio_generation_complete", "total_chunks": 5, "message": "Audio ready!"}
```

#### 3. Start Class (Teaching Content)
```json
// Send
{
    "type": "start_class",
    "course_id": "1",
    "module_index": 0,
    "sub_topic_index": 0,
    "language": "en-IN",
    "request_id": "optional_id"
}

// Receive (similar to chat_with_audio but with teaching content)
```

#### 4. Audio Only
```json
// Send
{
    "type": "audio_only",
    "text": "Text to convert to speech",
    "language": "en-IN"
}

// Receive
{"type": "audio_chunk", "chunk_id": 1, "audio_data": "base64_audio"}
{"type": "audio_generation_complete", "total_chunks": 3}
```

## 🔧 Available Services

The WebSocket server provides these services:
- **Chat Service**: AI-powered question answering
- **Audio Service**: Text-to-speech conversion with streaming
- **Teaching Service**: Educational content generation

## 📁 Project Structure

```
Prof_AI/
├── run_profai_websocket.py          # Main server startup script
├── websocket_server.py              # WebSocket server implementation
├── test_websocket_connection.py     # Connection test script
├── requirements.txt                 # Simplified dependencies
├── services/                        # AI services
│   ├── chat_service.py
│   ├── audio_service.py
│   └── teaching_service.py
├── websocket_tests/                 # HTML test files
│   ├── profai-websocket-test.html
│   ├── stream-test.html
│   └── websocket-status.html
└── data/                           # Course data and vector stores
```

## 🎯 What Was Removed

- FastAPI web server (port 5001)
- All HTML web interfaces (except WebSocket tests)
- REST API endpoints
- Web-related dependencies (FastAPI, uvicorn, etc.)
- Gunicorn configuration

## 🔌 WebSocket Test Files

HTML test files are available in the `websocket_tests/` directory:
- `profai-websocket-test.html` - Comprehensive WebSocket testing interface
- `stream-test.html` - Audio streaming test
- `websocket-status.html` - Connection status monitoring

Open these files in a web browser and connect to `ws://localhost:8765` to test the WebSocket functionality.

## 🚨 Troubleshooting

1. **Connection Refused**: Make sure the WebSocket server is running
2. **Service Errors**: Check your API keys in the `.env` file
3. **Audio Issues**: Verify the Sarvam API key for text-to-speech
4. **Port Conflicts**: Change `WEBSOCKET_PORT` in `.env` if 8765 is in use

## 📊 Performance

The WebSocket server is optimized for:
- Sub-300ms first audio chunk latency
- Real-time audio streaming
- Concurrent client connections
- Low memory footprint without web server overhead
