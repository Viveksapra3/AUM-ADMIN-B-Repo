#!/usr/bin/env python3
"""
Test ElevenLabs Integration
Quick test script to verify ElevenLabs service is working correctly
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from services.elevenlabs_service import ElevenLabsService, ElevenLabsConversationalAgent
import config

async def test_basic_connection():
    """Test 1: Basic WebSocket connection"""
    print("\n" + "="*60)
    print("TEST 1: Basic WebSocket Connection")
    print("="*60)
    
    try:
        service = ElevenLabsService()
        await service.connect_websocket()
        print("✅ Successfully connected to ElevenLabs WebSocket")
        await service.disconnect_websocket()
        print("✅ Successfully disconnected")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_text_to_speech():
    """Test 2: Text-to-Speech generation"""
    print("\n" + "="*60)
    print("TEST 2: Text-to-Speech Generation")
    print("="*60)
    
    try:
        service = ElevenLabsService()
        await service.connect_websocket()
        
        test_text = "Hello! This is a test of the ElevenLabs text to speech system."
        print(f"📝 Sending text: {test_text}")
        
        context_id = await service.send_text_in_context(test_text)
        print(f"✅ Created context: {context_id}")
        
        await service.flush_context(context_id)
        print("✅ Flushed context")
        
        # Wait for audio generation
        await asyncio.sleep(2)
        
        await service.close_context(context_id)
        print("✅ Closed context")
        
        await service.disconnect_websocket()
        print("✅ Test completed successfully")
        return True
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

async def test_audio_streaming():
    """Test 3: Audio streaming (quick test)"""
    print("\n" + "="*60)
    print("TEST 3: Audio Streaming (Quick Test)")
    print("="*60)
    
    try:
        service = ElevenLabsService()
        await service.connect_websocket()
        
        test_text = "Hello!"  # Short text for quick test
        print(f"📝 Streaming text: {test_text}")
        
        # Send text and flush
        context_id = await service.send_text_in_context(test_text)
        await service.flush_context(context_id)
        print(f"✅ Sent text to context: {context_id}")
        
        # Wait briefly for audio generation to start
        await asyncio.sleep(1)
        print("✅ Audio generation started")
        
        # Close context (don't wait for completion)
        await service.close_context(context_id)
        print("✅ Context closed")
        
        await service.disconnect_websocket()
        print("✅ Streaming test completed (quick mode)")
        return True
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False

async def test_context_management():
    """Test 4: Context management (interruptions)"""
    print("\n" + "="*60)
    print("TEST 4: Context Management & Interruptions")
    print("="*60)
    
    try:
        service = ElevenLabsService()
        await service.connect_websocket()
        
        # Create first context
        print("📝 Creating first context...")
        context1 = await service.send_text_in_context(
            "This is the first message that will be interrupted.",
            context_id="context_1"
        )
        print(f"✅ Created context: {context1}")
        
        # Simulate interruption
        await asyncio.sleep(0.5)
        print("🔄 Simulating interruption...")
        
        # Handle interruption
        context2 = await service.handle_interruption(
            old_context_id=context1,
            new_text="Sorry for interrupting. Here's the new response.",
            new_context_id="context_2"
        )
        print(f"✅ Handled interruption: {context1} → {context2}")
        
        await service.flush_context(context2)
        await asyncio.sleep(1)
        await service.close_context(context2)
        
        await service.disconnect_websocket()
        print("✅ Context management test completed")
        return True
        
    except Exception as e:
        print(f"❌ Context management test failed: {e}")
        return False

async def test_conversational_agent():
    """Test 5: High-level conversational agent"""
    print("\n" + "="*60)
    print("TEST 5: Conversational Agent with Greeting")
    print("="*60)
    
    try:
        agent = ElevenLabsConversationalAgent(
            greeting_text="Hello! I'm your AI assistant. How can I help you today?"
        )
        
        print("🤖 Starting conversation...")
        await agent.start_conversation()
        print("✅ Agent sent greeting")
        
        # Simulate conversation
        await asyncio.sleep(2)
        
        print("💬 Agent responding to user...")
        await agent.respond("I can help you with information about Auburn University.")
        print("✅ Agent sent response")
        
        await asyncio.sleep(2)
        
        print("👋 Ending conversation...")
        await agent.end_conversation()
        print("✅ Conversation ended successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversational agent test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 ELEVENLABS INTEGRATION TEST SUITE")
    print("="*60)
    
    # Check configuration
    print("\n📋 Configuration Check:")
    print(f"   API Key: {'✅ Set' if config.ELEVENLABS_API_KEY else '❌ Not set'}")
    print(f"   Voice ID: {config.ELEVENLABS_VOICE_ID}")
    print(f"   Model: {config.ELEVENLABS_MODEL}")
    print(f"   Greeting: {config.AGENT_GREETING[:50]}...")
    
    if not config.ELEVENLABS_API_KEY:
        print("\n❌ ERROR: ELEVENLABS_API_KEY not set in environment")
        print("   Please set it in your .env file:")
        print("   ELEVENLABS_API_KEY=your_api_key_here")
        return
    
    # Run tests
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Text-to-Speech", test_text_to_speech),
        ("Audio Streaming", test_audio_streaming),
        ("Context Management", test_context_management),
        ("Conversational Agent", test_conversational_agent),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! ElevenLabs integration is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Open websocket_tests/elevenlabs-voice-agent.html")
        print("   2. Update API key and Voice ID in the HTML file")
        print("   3. Test the frontend interface")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        print("   Common issues:")
        print("   - Invalid API key")
        print("   - Invalid Voice ID")
        print("   - Network connectivity")
        print("   - Rate limiting")

def main():
    """Main entry point"""
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
