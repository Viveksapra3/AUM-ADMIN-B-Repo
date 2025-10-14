"""
ElevenLabs Direct Audio Service
Uses standard WebSocket API without requiring agent configuration
"""

import asyncio
import json
import base64
import logging
from typing import Optional, Callable, AsyncGenerator
import websockets
from websockets.exceptions import ConnectionClosed
import config
from openai import OpenAI
import requests

logging.basicConfig(level=logging.INFO)

class ElevenLabsDirectService:
    """
    Direct ElevenLabs service using standard APIs.
    No agent configuration required.
    """
    
    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.voice_id = config.ELEVENLABS_VOICE_ID
        self.model = config.ELEVENLABS_MODEL
        self.websocket = None
        
        # OpenAI client for custom LLM
        # Add default timeouts to avoid TLS stalls
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY, timeout=30.0)
        self.custom_model = "ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T"
        
        # Conversation history
        self.conversation_history = []
        
        logging.info("✅ ElevenLabs Direct Service initialized")
    
    async def connect_tts_websocket(self) -> bool:
        """
        Deprecated: previously used persistent WS. Kept for backward compatibility.
        Always returns False to indicate per-request sockets should be used.
        """
        logging.info("ℹ️ connect_tts_websocket() is deprecated; using per-request sockets")
        return False
    
    async def transcribe_audio(self, audio_bytes: bytes, language: str = "en") -> str:
        """
        Transcribe audio using OpenAI Whisper API.
        
        Args:
            audio_bytes: Audio data (PCM16, 16kHz, mono)
            language: Language code
            
        Returns:
            Transcribed text
        """
        try:
            # Convert PCM16 to WAV format for Whisper
            import io
            import wave
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_bytes)
            
            wav_buffer.seek(0)
            wav_buffer.name = "audio.wav"
            
            # Call Whisper API
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=wav_buffer,
                language=language if language != "auto" else None
            )
            
            transcribed_text = transcript.text.strip()
            logging.info(f"🎤 Transcribed: {transcribed_text}")
            return transcribed_text
            
        except Exception as e:
            logging.error(f"❌ STT error: {e}")
            return ""
    
    async def get_llm_response(self, user_message: str) -> str:
        """
        Get response from custom fine-tuned LLM.
        
        Args:
            user_message: User's message
            
        Returns:
            LLM response text
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Build messages
            messages = [
                {"role": "system", "content": config.AGENT_GREETING}
            ] + self.conversation_history
            
            # Call custom model
            response = self.openai_client.chat.completions.create(
                model=self.custom_model,
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            llm_response = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": llm_response
            })
            
            logging.info(f"🤖 LLM Response: {llm_response[:100]}...")
            return llm_response
            
        except Exception as e:
            logging.error(f"❌ LLM error: {e}")
            return "I apologize, but I'm having trouble processing your request. Could you please try again?"
    
    async def text_to_speech_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Convert text to speech and stream audio chunks using a fresh ElevenLabs
        stream-input WebSocket per request. Falls back to REST TTS on error.
        """
        # Use the Multi-Context WebSocket endpoint with explicit output format
        url = (
            f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/multi-stream-input"
            f"?model_id={self.model}&output_format=mp3_44100_128&optimize_streaming_latency=3&auto_mode=true"
        )

        try:
            async with websockets.connect(
                url,
                additional_headers={"xi-api-key": self.api_key},
                max_size=16 * 1024 * 1024,
                ping_interval=25,
                ping_timeout=15,
            ) as ws:
                # Initial context configuration
                context_id = "conv_1"
                init_msg = {
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                    "context_id": context_id,
                }
                await ws.send(json.dumps(init_msg))

                # Send the text and then flush to finalize generation for this context
                await ws.send(json.dumps({"text": text, "context_id": context_id}))
                await ws.send(json.dumps({"flush": True, "context_id": context_id}))

                # Receive audio frames until final
                total_received = 0
                message_count = 0
                async for message in ws:
                    message_count += 1
                    try:
                        data = json.loads(message)
                        logging.info(f"📨 ElevenLabs message #{message_count}: {data}")
                        if data.get("audio"):
                            audio_bytes = base64.b64decode(data["audio"])
                            if audio_bytes:
                                total_received += len(audio_bytes)
                                logging.info(f"🎵 Audio chunk: {len(audio_bytes)} bytes")
                                yield audio_bytes
                        # Handle either is_final or isFinal markers from API variants
                        if data.get("is_final") or data.get("isFinal"):
                            logging.info("🏁 ElevenLabs marked final")
                            break
                    except json.JSONDecodeError:
                        # Binary audio payload
                        if isinstance(message, bytes) and len(message) > 0:
                            total_received += len(message)
                            logging.info(f"🎵 Binary audio: {len(message)} bytes")
                            yield message
                
                # If no audio was received, force fallback
                if total_received == 0:
                    logging.warning("⚠️ ElevenLabs streaming returned 0 bytes, forcing fallback")
                    raise Exception("No audio data received from streaming")

        except Exception as e:
            logging.error(f"❌ TTS streaming error: {e}")
            # REST fallback to avoid silent failures
            try:
                logging.info("🔄 Falling back to REST TTS...")
                audio = await self.text_to_speech(text)
                if audio:
                    logging.info(f"✅ REST TTS fallback: {len(audio)} bytes")
                    yield audio
                else:
                    logging.error("❌ REST TTS fallback also failed")
            except Exception as e2:
                logging.error(f"❌ TTS fallback error: {e2}")
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech (non-streaming).
        
        Args:
            text: Text to convert
            
        Returns:
            Complete audio as bytes
        """
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=(10, 60))
            response.raise_for_status()
            
            logging.info(f"✅ Generated audio: {len(response.content)} bytes")
            return response.content
            
        except Exception as e:
            logging.error(f"❌ TTS error: {e}")
            return b""
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        # Persistent WS is no longer used; nothing to do.
        self.websocket = None
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logging.info("🧹 Cleared conversation history")
