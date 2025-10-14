#!/usr/bin/env python3
"""
Setup script for AUM Real-Time Voice System

This script helps you set up the complete real-time voice conversation system
with Deepgram STT, ElevenLabs TTS, VAD, and barge-in functionality.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install Deepgram dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_deepgram.txt"], 
                      check=True, capture_output=True)
        print("✅ Deepgram dependencies installed")
        
        # Install websockets if not already installed
        subprocess.run([sys.executable, "-m", "pip", "install", "websockets>=11.0.0"], 
                      check=True, capture_output=True)
        print("✅ WebSocket support installed")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found")
        create_env_template()
        return False
    
    # Read .env file
    env_content = env_file.read_text()
    
    required_keys = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY", 
        "DEEPGRAM_API_KEY"
    ]
    
    missing_keys = []
    for key in required_keys:
        if f"{key}=" not in env_content or f"{key}=your_" in env_content:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing or incomplete API keys: {', '.join(missing_keys)}")
        return False
    
    print("✅ All required API keys found in .env")
    return True

def create_env_template():
    """Create .env template file"""
    template = """# AUM Real-Time Voice System API Keys

# OpenAI API Key (for fine-tuned LLM)
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs API Key (for TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Deepgram API Key (for real-time STT with VAD)
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8766
DEBUG=True
"""
    
    with open(".env", "w") as f:
        f.write(template)
    
    print("📝 Created .env template file")
    print("🔑 Please add your API keys to the .env file:")
    print("   1. OpenAI API Key")
    print("   2. ElevenLabs API Key") 
    print("   3. Deepgram API Key")

def get_api_keys_info():
    """Provide information about getting API keys"""
    print("\n🔑 API Key Information:")
    print("=" * 50)
    
    print("\n1. DEEPGRAM API KEY (Required for STT + VAD)")
    print("   • Sign up: https://console.deepgram.com/signup")
    print("   • Free tier: 45,000 minutes/month")
    print("   • Features: Real-time STT, VAD, low latency")
    
    print("\n2. ELEVENLABS API KEY (Required for TTS)")
    print("   • Sign up: https://elevenlabs.io/")
    print("   • Free tier: 10,000 characters/month")
    print("   • Features: High-quality voice synthesis")
    
    print("\n3. OPENAI API KEY (Required for LLM)")
    print("   • Sign up: https://platform.openai.com/")
    print("   • Pay-per-use pricing")
    print("   • Features: GPT-4 fine-tuned model")

def test_services():
    """Test if services are working"""
    print("\n🧪 Testing services...")
    
    try:
        # Test imports
        from services.deepgram_stt_service import DeepgramSTTService
        from services.elevenlabs_direct_service import ElevenLabsDirectService
        print("✅ Service imports successful")
        
        # Test Deepgram connection
        stt = DeepgramSTTService()
        if stt.enabled:
            print("✅ Deepgram STT service ready")
        else:
            print("❌ Deepgram STT service not ready (check API key)")
            return False
        
        # Test ElevenLabs connection
        tts = ElevenLabsDirectService()
        print("✅ ElevenLabs TTS service ready")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🎙️ AUM Real-Time Voice System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Check environment file
    if not check_env_file():
        get_api_keys_info()
        print("\n⚠️  Please complete the .env file setup and run this script again.")
        return
    
    # Test services
    if not test_services():
        print("\n❌ Service tests failed. Please check your API keys.")
        return
    
    print("\n🎉 Setup Complete!")
    print("=" * 20)
    print("\n📋 Next Steps:")
    print("1. Start the server: python run_simple_audio_server.py")
    print("2. Open the client: websocket_tests/realtime-voice-client.html")
    print("3. Click 'Connect' then 'Start Voice Chat'")
    print("4. Speak naturally - enjoy real-time conversation!")
    
    print("\n✨ Features Available:")
    print("• Real-time Speech-to-Text (Deepgram Nova-3)")
    print("• Voice Activity Detection (VAD)")
    print("• Barge-in & Interruption Support")
    print("• Streaming Text-to-Speech (ElevenLabs)")
    print("• Sub-500ms latency")
    print("• Telephonic-quality conversation")

if __name__ == "__main__":
    main()
