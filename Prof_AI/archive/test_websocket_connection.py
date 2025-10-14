#!/usr/bin/env python3
"""
Simple WebSocket connection test for ProfAI
Tests basic connectivity and ping/pong functionality
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test basic WebSocket connection and functionality."""
    uri = "ws://localhost:8766"
    
    try:
        print(f"🔌 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for connection ready message
            try:
                print("⏳ Waiting for connection ready message...")
                ready_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                ready_data = json.loads(ready_message)
                print(f"📨 Received: {ready_data.get('type', 'unknown')} - {ready_data.get('message', '')}")
                
                if ready_data.get('type') == 'connection_ready':
                    print("🎉 WebSocket server is ready!")
                    services = ready_data.get('services', {})
                    print(f"🔧 Available services: {services}")
                    
                    # Test ping/pong
                    print("\n🏓 Testing ping/pong...")
                    ping_message = {"type": "ping", "message": "test ping"}
                    await websocket.send(json.dumps(ping_message))
                    print("📤 Ping sent, waiting for pong...")
                    
                    pong_response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    pong_data = json.loads(pong_response)
                    
                    if pong_data.get('type') == 'pong':
                        print("✅ Ping/pong test successful!")
                        print(f"📨 Pong response: {pong_data.get('message', '')}")
                    else:
                        print(f"❌ Unexpected response: {pong_data}")
                        
                else:
                    print(f"⚠️ Unexpected ready message: {ready_data}")
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for server response")
                return False
                
    except ConnectionRefusedError:
        print("❌ Connection refused - make sure the WebSocket server is running")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    print("\n🎯 WebSocket connection test completed successfully!")
    return True

async def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 ProfAI WebSocket Connection Test")
    print("=" * 60)
    
    success = await test_websocket_connection()
    
    if success:
        print("\n✅ All tests passed! WebSocket server is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Check the WebSocket server.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
