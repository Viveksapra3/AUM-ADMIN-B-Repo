#!/usr/bin/env python3
"""
Production Audio WebSocket Server
Handles browser ↔ ElevenLabs audio streaming with custom LLM
"""

import asyncio
import json
import logging
import base64
import websockets
from websockets.exceptions import ConnectionClosed
from services.elevenlabs_conversational_service import ElevenLabsConversationalService
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AudioWebSocketServer:
    """Production audio WebSocket server."""
    
    def __init__(self, host="0.0.0.0", port=8766):
        self.host = host
        self.port = port
        self.active_connections = {}
    
    async def handle_client(self, websocket):
        """Handle incoming client WebSocket connection."""
        client_id = id(websocket)
        logging.info(f"🔌 Client {client_id} connected from {websocket.remote_address}")
        
        # Create ElevenLabs service for this client
        elevenlabs_service = ElevenLabsConversationalService()
        
        self.active_connections[client_id] = {
            'websocket': websocket,
            'service': elevenlabs_service,
            'language': 'en'  # Default language
        }
        
        try:
            # Send connection ready message
            await websocket.send(json.dumps({
                'type': 'connection_ready',
                'message': 'Connected to AUM Voice Agent',
                'client_id': str(client_id)
            }))
            
            # Handle incoming messages from client
            async for message in websocket:
                try:
                    # Try to parse as JSON
                    data = json.loads(message)
                    await self.handle_client_message(client_id, data)
                except json.JSONDecodeError:
                    # Binary audio data
                    if isinstance(message, bytes):
                        await self.handle_client_audio(client_id, message)
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
                    service = self.active_connections[client_id]['service']
                    await service.disconnect()
                except:
                    pass
                del self.active_connections[client_id]
            logging.info(f"🧹 Cleaned up client {client_id}")
    
    async def handle_client_message(self, client_id, data):
        """Handle JSON messages from client."""
        connection = self.active_connections.get(client_id)
        if not connection:
            return
        
        websocket = connection['websocket']
        service = connection['service']
        
        message_type = data.get('type')
        
        if message_type == 'start_conversation':
            # Start conversation with ElevenLabs
            language = data.get('language', 'en')
            connection['language'] = language
            
            logging.info(f"🎙️ Starting conversation for client {client_id} (Language: {language})")
            
            # Connect to ElevenLabs
            conversation_id = await service.connect(language=language)
            
            # Send confirmation
            await websocket.send(json.dumps({
                'type': 'conversation_started',
                'conversation_id': conversation_id,
                'language': language
            }))
            
            # Start handling ElevenLabs messages
            asyncio.create_task(self.handle_elevenlabs_messages(client_id))
        
        elif message_type == 'audio':
            # Audio from client (user speaking)
            audio_base64 = data.get('audio')
            if audio_base64:
                audio_bytes = base64.b64decode(audio_base64)
                await service.send_audio(audio_bytes)
        
        elif message_type == 'text':
            # Text input from client
            text = data.get('text', '')
            await service.send_text(text)
        
        elif message_type == 'change_language':
            # Change conversation language
            new_language = data.get('language', 'en')
            connection['language'] = new_language
            
            # Reconnect with new language
            await service.disconnect()
            conversation_id = await service.connect(language=new_language)
            
            await websocket.send(json.dumps({
                'type': 'language_changed',
                'language': new_language,
                'conversation_id': conversation_id
            }))
        
        elif message_type == 'ping':
            # Keep-alive ping
            await websocket.send(json.dumps({'type': 'pong'}))
        
        elif message_type == 'disconnect':
            # Client wants to disconnect
            await service.disconnect()
            await websocket.close()
    
    async def handle_client_audio(self, client_id, audio_bytes):
        """Handle binary audio from client."""
        connection = self.active_connections.get(client_id)
        if not connection:
            return
        
        service = connection['service']
        await service.send_audio(audio_bytes)
    
    async def handle_elevenlabs_messages(self, client_id):
        """Handle messages from ElevenLabs and forward to client."""
        connection = self.active_connections.get(client_id)
        if not connection:
            return
        
        websocket = connection['websocket']
        service = connection['service']
        
        async def on_audio(audio_bytes):
            """Forward audio to client."""
            try:
                # Send as base64 JSON
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                await websocket.send(json.dumps({
                    'type': 'audio',
                    'audio': audio_base64
                }))
            except Exception as e:
                logging.error(f"❌ Error sending audio to client: {e}")
        
        async def on_transcript(transcript):
            """Forward user transcript to client."""
            try:
                await websocket.send(json.dumps({
                    'type': 'user_transcript',
                    'text': transcript
                }))
            except Exception as e:
                logging.error(f"❌ Error sending transcript to client: {e}")
        
        async def on_agent_response(response):
            """Forward agent response to client."""
            try:
                await websocket.send(json.dumps({
                    'type': 'agent_response',
                    'text': response
                }))
            except Exception as e:
                logging.error(f"❌ Error sending response to client: {e}")
        
        try:
            await service.handle_messages(
                on_audio=on_audio,
                on_transcript=on_transcript,
                on_agent_response=on_agent_response
            )
        except Exception as e:
            logging.error(f"❌ Error handling ElevenLabs messages: {e}")
    
    async def start(self):
        """Start the WebSocket server."""
        logging.info(f"🚀 Starting Audio WebSocket Server on {self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10,
            max_size=16 * 1024 * 1024  # 16MB for audio
        ):
            logging.info(f"✅ Server running on ws://{self.host}:{self.port}")
            logging.info(f"📝 Waiting for client connections...")
            logging.info(f"🌍 Multi-language support: 32+ languages")
            logging.info(f"🤖 Custom LLM: ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T")
            
            # Run forever
            await asyncio.Future()

async def main():
    """Main entry point."""
    server = AudioWebSocketServer(
        host=config.HOST,
        port=8766
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
║        🎙️  AUM Audio WebSocket Server  🎙️                    ║
║                                                              ║
║  Server: ws://0.0.0.0:8766                                  ║
║  Frontend: ws://localhost:8766                              ║
║                                                              ║
║  Features:                                                   ║
║  ✅ Full-duplex audio streaming                             ║
║  ✅ Speech-to-Text (32+ languages)                          ║
║  ✅ Text-to-Speech (ElevenLabs)                             ║
║  ✅ Custom LLM (GPT-4.1-mini fine-tuned)                    ║
║  ✅ Voice Activity Detection                                ║
║  ✅ Multi-language support                                  ║
║                                                              ║
║  Press Ctrl+C to stop                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
