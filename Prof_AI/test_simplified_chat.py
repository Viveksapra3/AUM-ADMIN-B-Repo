#!/usr/bin/env python3
"""
Test simplified chat service without RAG
"""

import asyncio
import websockets
import json
import sys

async def test_chat_functionality():
    """Test the simplified chat service."""
    uri = "ws://localhost:8766"
    
    try:
        print(f"🔌 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for connection ready message
            ready_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            ready_data = json.loads(ready_message)
            print(f"📨 Connection ready: {ready_data.get('message', '')}")
            
            # Test AUM counselor chat
            print("\n💬 Testing AUM Counselor Service...")
            chat_message = {
                "type": "chat_with_audio",
                "message": "Hello, I want to know about admission requirements for AUM",
                "language": "en-IN",
                "request_id": "test_001"
            }
            
            await websocket.send(json.dumps(chat_message))
            print("📤 Chat message sent")
            
            # Collect responses
            responses = []
            timeout_count = 0
            max_responses = 5  # Expect: processing_started, text_response, audio_generation_started, audio_chunk(s), audio_complete
            
            while len(responses) < max_responses and timeout_count < 3:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    response_data = json.loads(response)
                    responses.append(response_data)
                    
                    msg_type = response_data.get('type', 'unknown')
                    print(f"📨 Received: {msg_type}")
                    
                    if msg_type == "text_response":
                        text = response_data.get('text', '')
                        print(f"   💬 Text: {text[:150]}{'...' if len(text) > 150 else ''}")
                        metadata = response_data.get('metadata', {})
                        sources = metadata.get('sources', ['Unknown'])
                        counselor = metadata.get('counselor', 'Unknown')
                        print(f"   📚 Sources: {sources}")
                        print(f"   👨‍🎓 Counselor: {counselor}")
                    
                    elif msg_type == "audio_chunk":
                        chunk_id = response_data.get('chunk_id', 0)
                        size = response_data.get('size', 0)
                        is_first = response_data.get('is_first_chunk', False)
                        print(f"   🎵 Audio chunk {chunk_id}: {size} bytes {'(FIRST)' if is_first else ''}")
                    
                    elif msg_type == "audio_generation_complete":
                        total_chunks = response_data.get('total_chunks', 0)
                        latency = response_data.get('first_chunk_latency', 0)
                        print(f"   ✅ Audio complete: {total_chunks} chunks, first chunk in {latency:.0f}ms")
                        break
                    
                    elif msg_type == "error":
                        error_msg = response_data.get('error', 'Unknown error')
                        print(f"   ❌ Error: {error_msg}")
                        return False
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"   ⏰ Timeout {timeout_count}/3")
                    if timeout_count >= 3:
                        break
            
            print(f"\n📊 Received {len(responses)} responses")
            
            # Check if we got the expected responses
            response_types = [r.get('type') for r in responses]
            expected_types = ['processing_started', 'text_response', 'audio_generation_started']
            
            success = all(expected_type in response_types for expected_type in expected_types)
            
            if success:
                print("✅ AUM Counselor test successful - got text response and audio generation!")
            else:
                print(f"⚠️ Partial success - got response types: {response_types}")
                
            return success
                
    except ConnectionRefusedError:
        print("❌ Connection refused - make sure the WebSocket server is running")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

async def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 ProfAI AUM Counselor Only Test")
    print("=" * 60)
    
    success = await test_chat_functionality()
    
    if success:
        print("\n✅ AUM Counselor service is working correctly!")
        print("🎉 All responses now come from Alex - AUM International Admission Counselor")
        sys.exit(0)
    else:
        print("\n❌ Chat test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
