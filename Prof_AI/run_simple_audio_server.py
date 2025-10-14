#!/usr/bin/env python3
"""
Simple Audio WebSocket Server
Text-based conversation with audio responses (no STT required)
"""

import asyncio
import json
import logging
import base64
import websockets
from websockets.exceptions import ConnectionClosed
from services.elevenlabs_direct_service import ElevenLabsDirectService
from services.deepgram_stt_service import DeepgramSTTService as StreamingSTTService
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SimpleAudioServer:
    """Simple audio server with text input and audio output."""
    
    def __init__(self, host="0.0.0.0", port=8766):
        self.host = host
        self.port = port
        self.active_connections = {}
    
    async def handle_client(self, websocket):
        """Handle incoming client WebSocket connection."""
        client_id = id(websocket)
        logging.info(f"🔌 Client {client_id} connected from {websocket.remote_address}")
        
        # Create ElevenLabs service for this client
        service = ElevenLabsDirectService()
        
        self.active_connections[client_id] = {
            'websocket': websocket,
            'service': service,
            'language': 'en',
            'stt': None,
            'stt_task': None
        }
        
        try:
            # Send connection ready message
            try:
                if websocket.close_code is not None:
                    return
                await websocket.send(json.dumps({
                    'type': 'connection_ready',
                    'message': 'Connected to AUM Voice Agent',
                    'client_id': str(client_id)
                }))
            except ConnectionClosed:
                return
            
            # Send greeting
            greeting = config.AGENT_GREETING
            try:
                if websocket.close_code is not None:
                    return
                await websocket.send(json.dumps({
                    'type': 'agent_response',
                    'text': greeting
                }))
            except ConnectionClosed:
                return
            
            # Generate and send greeting audio (non-streaming)
            logging.info(f"🎙️ Generating greeting audio...")
            try:
                audio_data = await service.text_to_speech(greeting)
                if audio_data:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    try:
                        if websocket.close_code is None:
                            await websocket.send(json.dumps({
                                'type': 'audio',
                                'audio': audio_base64
                            }))
                        logging.info(f"✅ Sent greeting audio: {len(audio_data)} bytes")
                    except ConnectionClosed:
                        pass
            except Exception as e:
                logging.error(f"❌ Error generating greeting audio: {e}")
            
            # Handle incoming messages from client
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(client_id, data)
                except json.JSONDecodeError:
                    logging.error(f"❌ Invalid JSON from client {client_id}")
                except Exception as e:
                    logging.error(f"❌ Error handling message: {e}")
                    
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
                    stt = self.active_connections[client_id].get('stt')
                    if stt:
                        await stt.close()
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
        
        if message_type == 'audio_transcribe':
            # Audio from client (user speaking) - transcribe it
            audio_base64 = data.get('audio')
            language = data.get('language', 'en')
            
            if not audio_base64:
                return
            
            logging.info(f"🎤 Received audio from client {client_id} for transcription")
            
            try:
                # Decode audio
                audio_bytes = base64.b64decode(audio_base64)
                
                # Transcribe using Whisper
                user_text = await service.transcribe_audio(audio_bytes, language)
                
                if not user_text:
                    logging.warning("⚠️ No transcription result")
                    return
                
                logging.info(f"💬 Transcribed: {user_text}")
                
                # Echo user message
                try:
                    if websocket.close_code is not None:
                        return
                    await websocket.send(json.dumps({
                        'type': 'user_transcript',
                        'text': user_text
                    }))
                except ConnectionClosed:
                    return
                
                # Get LLM response
                llm_response = await service.get_llm_response(user_text)
                
                # Send text response
                try:
                    if websocket.close_code is not None:
                        return
                    await websocket.send(json.dumps({
                        'type': 'agent_response',
                        'text': llm_response
                    }))
                except ConnectionClosed:
                    return
                
                # Generate and send audio (streaming)
                logging.info(f"🎙️ Generating audio response (streaming)...")
                total_bytes = 0
                async for chunk in service.text_to_speech_stream(llm_response):
                    if not chunk:
                        continue
                    total_bytes += len(chunk)
                    audio_base64 = base64.b64encode(chunk).decode('utf-8')
                    try:
                        if websocket.close_code is not None:
                            break
                        await websocket.send(json.dumps({
                            'type': 'audio_chunk',
                            'audio': audio_base64
                        }))
                    except ConnectionClosed:
                        break
                try:
                    if websocket.close_code is None:
                        await websocket.send(json.dumps({'type': 'audio_end'}))
                except ConnectionClosed:
                    pass
                logging.info(f"✅ Sent audio stream: {total_bytes} bytes")
                
            except Exception as e:
                logging.error(f"❌ Error processing audio: {e}")
                try:
                    if websocket.close_code is None:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': 'Sorry, I had trouble understanding that.'
                        }))
                except ConnectionClosed:
                    pass
        
        elif message_type == 'text':
            # User sent text input
            user_text = data.get('text', '').strip()
            if not user_text:
                return
            
            logging.info(f"💬 Client {client_id} said: {user_text}")
            
            # Echo user message
            try:
                if websocket.close_code is not None:
                    return
                await websocket.send(json.dumps({
                    'type': 'user_transcript',
                    'text': user_text
                }))
            except ConnectionClosed:
                return
            
            # Get LLM response
            try:
                llm_response = await service.get_llm_response(user_text)
                
                # Send text response
                try:
                    if websocket.close_code is not None:
                        return
                    await websocket.send(json.dumps({
                        'type': 'agent_response',
                        'text': llm_response
                    }))
                except ConnectionClosed:
                    return
                
                # Generate and send audio
                logging.info(f"🎙️ Generating audio response...")
                audio_data = await service.text_to_speech(llm_response)
                
                if audio_data:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    try:
                        if websocket.close_code is not None:
                            return
                        await websocket.send(json.dumps({
                            'type': 'audio',
                            'audio': audio_base64
                        }))
                        logging.info(f"✅ Sent audio: {len(audio_data)} bytes")
                    except ConnectionClosed:
                        return
                
            except Exception as e:
                logging.error(f"❌ Error processing message: {e}")
                try:
                    if websocket.close_code is None:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': 'Sorry, I encountered an error processing your request.'
                        }))
                except ConnectionClosed:
                    pass
        
        elif message_type == 'ping':
            # Keep-alive ping
            try:
                if websocket.close_code is None:
                    await websocket.send(json.dumps({'type': 'pong'}))
            except ConnectionClosed:
                pass
        
        elif message_type == 'disconnect':
            # Client wants to disconnect
            await service.disconnect()
            await websocket.close()

        elif message_type == 'stt_stream_start':
            language = data.get('language', 'auto')
            sample_rate = int(data.get('sample_rate', 16000))
            stt = StreamingSTTService(sample_rate=sample_rate, language_hint=None if language == 'auto' else language)
            if not stt.enabled:
                try:
                    if websocket.close_code is None:
                        await websocket.send(json.dumps({'type': 'stt_unavailable'}))
                except ConnectionClosed:
                    pass
                return
            ok = await stt.start()
            if not ok:
                try:
                    if websocket.close_code is None:
                        await websocket.send(json.dumps({'type': 'stt_unavailable'}))
                except ConnectionClosed:
                    pass
                return
            connection['stt'] = stt
            # Start event pump with VAD and barge-in support
            async def stt_event_pump(client_id_inner: int):
                conn = self.active_connections.get(client_id_inner)
                if not conn:
                    return
                ws = conn['websocket']
                stt_service = conn.get('stt')
                if not stt_service:
                    return
                
                # Track conversation state for barge-in
                conn['is_speaking'] = False
                conn['current_tts_task'] = None
                
                async for event in stt_service.recv():
                    etype = event.get('type')
                    text = event.get('text', '')
                    
                    if etype == 'speech_started':
                        # User started speaking - implement barge-in
                        logging.info("🗣️ User started speaking - enabling barge-in")
                        conn['is_speaking'] = True
                        logging.debug(f"🔧 is_speaking set to: {conn['is_speaking']}")
                        
                        # Cancel current TTS if playing
                        if conn.get('current_tts_task') and not conn['current_tts_task'].done():
                            logging.info("⏹️ Interrupting current TTS (barge-in)")
                            conn['current_tts_task'].cancel()
                            try:
                                await ws.send(json.dumps({'type': 'tts_interrupted'}))
                            except ConnectionClosed:
                                break
                        
                        try:
                            await ws.send(json.dumps({'type': 'speech_started'}))
                        except ConnectionClosed:
                            break
                            
                    elif etype == 'utterance_end':
                        # User stopped speaking
                        logging.info("🔇 User stopped speaking")
                        conn['is_speaking'] = False
                        logging.debug(f"🔧 is_speaking set to: {conn['is_speaking']}")
                        try:
                            await ws.send(json.dumps({'type': 'utterance_end'}))
                        except ConnectionClosed:
                            break
                            
                    elif etype == 'partial' and text:
                        try:
                            if ws.close_code is not None:
                                break
                            await ws.send(json.dumps({'type': 'partial_transcript', 'text': text}))
                        except ConnectionClosed:
                            break
                            
                    elif etype == 'final':
                        # Final transcript from STT - also ensure is_speaking is reset
                        logging.info(f"📝 Final transcript: {text}")
                        conn['is_speaking'] = False  # Safety: reset speaking state on final transcript
                        logging.debug(f"🔧 is_speaking reset to: {conn['is_speaking']} (final transcript)")
                        try:
                            await ws.send(json.dumps({'type': 'final_transcript', 'text': text, 'language': event.get('language', 'en')}))
                        except ConnectionClosed:
                            break
                        
                        # Process LLM and TTS streaming for final transcript
                        logging.info(f"🤖 Processing final transcript: {text}")
                        
                        try:
                            llm_response = await connection['service'].get_llm_response(text)
                            
                            try:
                                if ws.close_code is not None:
                                    return
                                await ws.send(json.dumps({'type': 'agent_response', 'text': llm_response}))
                            except ConnectionClosed:
                                return
                            
                            # Create TTS task (non-streaming) for potential cancellation
                            async def send_tts_response():
                                try:
                                    # If user already started speaking, skip generating TTS
                                    if conn.get('is_speaking', False):
                                        logging.info("🛑 Skipping TTS: user is speaking")
                                        return
                                    audio_data = await connection['service'].text_to_speech(llm_response)
                                    if not audio_data:
                                        return
                                    # If user started speaking during generation, skip sending
                                    if conn.get('is_speaking', False):
                                        logging.info("🛑 Skipping TTS send: user started speaking")
                                        return
                                    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                                    try:
                                        if ws.close_code is None:
                                            await ws.send(json.dumps({'type': 'audio', 'audio': audio_b64}))
                                    except ConnectionClosed:
                                        pass
                                    logging.info(f"✅ TTS completed: {len(audio_data)} bytes")
                                except asyncio.CancelledError:
                                    logging.info("🛑 TTS task cancelled (barge-in)")
                                    try:
                                        if ws.close_code is None:
                                            await ws.send(json.dumps({'type': 'tts_cancelled'}))
                                    except ConnectionClosed:
                                        pass
                                except Exception as e:
                                    logging.error(f"❌ TTS error: {e}")
                            
                            # Start TTS task
                            tts_task = asyncio.create_task(send_tts_response())
                            conn['current_tts_task'] = tts_task
                            
                            # Wait for completion or cancellation
                            try:
                                await tts_task
                            except asyncio.CancelledError:
                                pass
                            finally:
                                conn['current_tts_task'] = None
                                
                        except Exception as e:
                            logging.error(f"❌ Error processing LLM response: {e}")
                            try:
                                if ws.close_code is None:
                                    await ws.send(json.dumps({
                                        'type': 'error',
                                        'message': 'Sorry, I had trouble processing that.'
                                    }))
                            except ConnectionClosed:
                                pass
            task = asyncio.create_task(stt_event_pump(client_id))
            connection['stt_task'] = task
            try:
                if websocket.close_code is None:
                    await websocket.send(json.dumps({'type': 'stt_ready'}))
            except ConnectionClosed:
                pass

        elif message_type == 'stt_audio_chunk':
            stt = connection.get('stt')
            if not stt:
                return
            audio_base64 = data.get('audio')
            if not audio_base64:
                return
            try:
                pcm_bytes = base64.b64decode(audio_base64)
            except Exception:
                return
            # Debug log to verify audio flow and chunk sizes
            try:
                logging.debug(f"🎧 STT chunk received: {len(pcm_bytes)} bytes")
            except Exception:
                pass
            await stt.send_audio_chunk(pcm_bytes)

        elif message_type == 'stt_stream_end':
            stt = connection.get('stt')
            if stt:
                await stt.close()
                connection['stt'] = None
            t = connection.get('stt_task')
            if t and not t.done():
                try:
                    t.cancel()
                except Exception:
                    pass
                connection['stt_task'] = None
    
    async def start(self):
        """Start the WebSocket server."""
        logging.info(f"🚀 Starting Simple Audio WebSocket Server on {self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=30,
            ping_timeout=10,
            max_size=16 * 1024 * 1024
        ):
            logging.info(f"✅ Server running on ws://{self.host}:{self.port}")
            logging.info(f"📝 Mode: Text input → Audio output")
            logging.info(f"🤖 Custom LLM: ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T")
            
            # Run forever
            await asyncio.Future()

async def main():
    """Main entry point."""
    server = SimpleAudioServer(
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
║        🎙️  AUM Real-Time Voice Server  🎙️                   ║
║                                                              ║
║  Server: ws://0.0.0.0:8766                                  ║
║  Mode: Real-time Voice Conversation                         ║
║                                                              ║
║  Features:                                                   ║
║  ✅ Real-time STT (Deepgram Nova-3)                        ║
║  ✅ Streaming TTS (ElevenLabs)                              ║
║  ✅ Voice Activity Detection (VAD)                          ║
║  ✅ Barge-in & Interruption Support                         ║
║  ✅ Custom LLM (GPT-4.1-mini fine-tuned)                    ║
║  ✅ Sub-500ms latency                                       ║
║                                                              ║
║  Note: Telephonic-quality real-time conversation!           ║
║                                                              ║
║  Press Ctrl+C to stop                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
