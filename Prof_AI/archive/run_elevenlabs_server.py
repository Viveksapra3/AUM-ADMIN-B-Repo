#!/usr/bin/env python3
"""
ElevenLabs WebSocket Server
Runs on port 8766 and proxies between browser clients and ElevenLabs API
"""

import asyncio
import json
import logging
import websockets
from websockets.exceptions import ConnectionClosed
from services.elevenlabs_service import ElevenLabsService, ElevenLabsConversationalAgent
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ElevenLabsWebSocketServer:
    """WebSocket server that proxies between browser and ElevenLabs."""
    
    def __init__(self, host="0.0.0.0", port=8766):
        self.host = host
        self.port = port
        self.active_connections = {}
        
    async def handle_client(self, websocket):
        """Handle incoming client WebSocket connection."""
        client_id = id(websocket)
        logging.info(f"🔌 Client {client_id} connected from {websocket.remote_address}")
        
        # Create ElevenLabs service for this client
        elevenlabs_service = ElevenLabsService()
        agent = ElevenLabsConversationalAgent()
        
        self.active_connections[client_id] = {
            'websocket': websocket,
            'service': elevenlabs_service,
            'agent': agent
        }
        
        try:
            # Send connection ready message
            await websocket.send(json.dumps({
                'type': 'connection_ready',
                'message': 'Connected to ElevenLabs Voice Agent',
                'client_id': str(client_id)
            }))
            
            # Start conversation with greeting
            logging.info(f"👋 Starting conversation for client {client_id}")
            await agent.start_conversation()
            
            # Send greeting notification
            await websocket.send(json.dumps({
                'type': 'agent_speaking',
                'text': config.AGENT_GREETING,
                'context_id': agent.current_context_id
            }))
            
            # Handle incoming messages from client
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(client_id, data)
                except json.JSONDecodeError:
                    logging.error(f"❌ Invalid JSON from client {client_id}")
                except Exception as e:
                    logging.error(f"❌ Error handling message from client {client_id}: {e}")
                    
        except ConnectionClosed:
            logging.info(f"🔌 Client {client_id} disconnected")
        except Exception as e:
            logging.error(f"❌ Error with client {client_id}: {e}")
        finally:
            # Cleanup
            if client_id in self.active_connections:
                try:
                    await agent.end_conversation()
                except:
                    pass
                del self.active_connections[client_id]
            logging.info(f"🧹 Cleaned up client {client_id}")
    
    async def handle_client_message(self, client_id, data):
        """Handle messages from client."""
        connection = self.active_connections.get(client_id)
        if not connection:
            return
        
        websocket = connection['websocket']
        agent = connection['agent']
        
        message_type = data.get('type')
        
        if message_type == 'user_text':
            # User sent text (from STT or typing)
            user_text = data.get('text', '')
            logging.info(f"💬 Client {client_id} said: {user_text}")
            
            # Get response from your AUM Counselor (you can integrate here)
            # For now, just echo back
            response_text = f"I heard you say: {user_text}. How can I help you with that?"
            
            # Send response through agent
            context_id = await agent.respond(response_text)
            
            # Notify client
            await websocket.send(json.dumps({
                'type': 'agent_speaking',
                'text': response_text,
                'context_id': context_id
            }))
            
        elif message_type == 'user_speaking':
            # User started speaking (VAD detected)
            logging.info(f"🎤 Client {client_id} started speaking")
            
            # If agent is speaking, interrupt
            if agent.is_speaking:
                # Will handle interruption when we get the text
                pass
                
        elif message_type == 'ping':
            # Keep-alive ping
            await websocket.send(json.dumps({'type': 'pong'}))
            
        elif message_type == 'disconnect':
            # Client wants to disconnect
            await agent.end_conversation()
            await websocket.close()
    
    async def start(self):
        """Start the WebSocket server."""
        logging.info(f"🚀 Starting ElevenLabs WebSocket Server on {self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10
        ):
            logging.info(f"✅ Server running on ws://{self.host}:{self.port}")
            logging.info(f"📝 Waiting for client connections...")
            
            # Run forever
            await asyncio.Future()  # Run forever

async def main():
    """Main entry point."""
    server = ElevenLabsWebSocketServer(
        host=config.HOST,
        port=8766  # Use port 8766 for ElevenLabs
    )
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logging.info("\n⚠️ Server stopped by user")
    except Exception as e:
        logging.error(f"❌ Server error: {e}")
        raise

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎙️  ElevenLabs Voice Agent WebSocket Server  🎙️       ║
║                                                              ║
║  Server will run on: ws://0.0.0.0:8766                      ║
║  Frontend connects to: ws://localhost:8766                  ║
║                                                              ║
║  Press Ctrl+C to stop                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
