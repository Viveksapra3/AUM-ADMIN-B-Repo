#!/bin/bash

# AUM Voice Agent - Quick Start Script
# This script starts both servers needed for the voice agent

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🎙️  AUM Voice Agent - Quick Start  🎙️                 ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create .env with your API keys:"
    echo "  ELEVENLABS_API_KEY=your_key"
    echo "  OPENAI_API_KEY=your_key"
    echo ""
fi

# Kill any existing processes on ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8766 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start the WebSocket server in background
echo "🚀 Starting WebSocket server on port 8766..."
python run_simple_audio_server.py &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ WebSocket server started (PID: $SERVER_PID)"
else
    echo "❌ Failed to start WebSocket server"
    exit 1
fi

# Start HTTP server for client files
echo "🌐 Starting HTTP server on port 8000..."
cd websocket_tests
python3 -m http.server 8000 &
HTTP_PID=$!
cd ..

# Wait for HTTP server to start
sleep 1

# Check if HTTP server started successfully
if ps -p $HTTP_PID > /dev/null; then
    echo "✅ HTTP server started (PID: $HTTP_PID)"
else
    echo "❌ Failed to start HTTP server"
    kill $SERVER_PID
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║  ✅ Both servers are running!                                ║"
echo "║                                                              ║"
echo "║  📊 WebSocket Server: ws://localhost:8766                   ║"
echo "║  🌐 HTTP Server: http://localhost:8000                      ║"
echo "║                                                              ║"
echo "║  🎭 Avatar Client (Voice + VAD):                            ║"
echo "║     http://localhost:8000/avatar-audio-client.html          ║"
echo "║                                                              ║"
echo "║  📝 Simple Client (Text):                                   ║"
echo "║     http://localhost:8000/simple-audio-client.html          ║"
echo "║                                                              ║"
echo "║  🛑 To stop: Press Ctrl+C                                   ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Try to open browser automatically
if command -v open &> /dev/null; then
    echo "🌐 Opening avatar client in browser..."
    sleep 1
    open http://localhost:8000/avatar-audio-client.html
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $SERVER_PID 2>/dev/null
    kill $HTTP_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for user to stop
echo "Press Ctrl+C to stop all servers..."
wait
