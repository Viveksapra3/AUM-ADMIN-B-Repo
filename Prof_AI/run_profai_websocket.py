#!/usr/bin/env python3
"""
ProfAI WebSocket Server Startup Script
Starts only the WebSocket server on port 8765
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys, '_clear_type_cache'):
    sys._clear_type_cache()

# Clear any existing module cache for our services
modules_to_clear = [mod for mod in sys.modules if 'sarvam' in mod.lower()]
for mod in modules_to_clear:
    del sys.modules[mod]

async def start_websocket_server_async(host, port):
    """Start WebSocket server asynchronously."""
    from websocket_server import start_websocket_server
    
    print(f"🌐 Starting WebSocket server on ws://{host}:{port}")
    await start_websocket_server(host, port)

def main():
    """Main startup function."""
    websocket_host = os.getenv("WEBSOCKET_HOST", "0.0.0.0")
    websocket_port = int(os.getenv("WEBSOCKET_PORT", 8765))

    print("=" * 60)
    print("🎓 ProfAI - WebSocket Server Only")
    print("=" * 60)

    try:
        import socket

        def check_port(host, port, name):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                print(f"⚠️  Warning: Port {port} ({name}) appears to be in use.")
                return False
            return True

        if not check_port(websocket_host, websocket_port, "WebSocket"):
            if input("\nContinue anyway? (y/N): ").lower().strip() != 'y':
                sys.exit(1)

        print(f"\n🌐 Starting WebSocket server on ws://{websocket_host}:{websocket_port}")
        print("=" * 60)
        print("✅ WebSocket server ready for connections")
        print(f"   - 🔌 Connect to: ws://{websocket_host}:{websocket_port}")
        print("=" * 60)

        asyncio.run(start_websocket_server_async(websocket_host, websocket_port))

    except KeyboardInterrupt:
        print("\n🛑 Shutting down WebSocket server...")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
