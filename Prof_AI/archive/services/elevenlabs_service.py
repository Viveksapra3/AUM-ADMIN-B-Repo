"""
ElevenLabs Service - Multi-Context WebSocket with VAD for Conversational AI
Replaces Sarvam AI with ElevenLabs for TTS, STT, and conversational features
"""

import asyncio
import json
import base64
import logging
from typing import Optional, AsyncGenerator
import websockets
from websockets.exceptions import ConnectionClosed
import config

class ElevenLabsService:
    """Service for ElevenLabs Conversational AI with Multi-Context WebSocket."""
    
    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.voice_id = config.ELEVENLABS_VOICE_ID
        self.model = config.ELEVENLABS_MODEL
        self.websocket = None
        self.context_counter = 0
        
        logging.info("✅ ElevenLabs Service initialized")
    
    def _get_websocket_url(self) -> str:
        """Get the WebSocket URL for multi-context streaming."""
        return f"wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/multi-stream-input?model_id={self.model}"
    
    async def connect_websocket(self):
        """Connect to ElevenLabs multi-context WebSocket."""
        try:
            url = self._get_websocket_url()
            self.websocket = await websockets.connect(
                url,
                additional_headers={
                    "xi-api-key": self.api_key
                },
                max_size=16 * 1024 * 1024,  # 16MB max message size
                ping_interval=30,
                ping_timeout=20
            )
            logging.info("✅ Connected to ElevenLabs WebSocket")
            return self.websocket
        except Exception as e:
            logging.error(f"❌ Failed to connect to ElevenLabs: {e}")
            raise
    
    async def disconnect_websocket(self):
        """Disconnect from ElevenLabs WebSocket."""
        if self.websocket:
            try:
                await self.websocket.send(json.dumps({"close_socket": True}))
                await self.websocket.close()
                logging.info("🔌 Disconnected from ElevenLabs WebSocket")
            except Exception as e:
                logging.error(f"Error disconnecting: {e}")
    
    def _generate_context_id(self) -> str:
        """Generate unique context ID."""
        self.context_counter += 1
        return f"context_{self.context_counter}"
    
    async def send_text_in_context(
        self, 
        text: str, 
        context_id: Optional[str] = None,
        voice_settings: Optional[dict] = None
    ) -> str:
        """
        Send text to be synthesized in a specific context.
        
        Args:
            text: Text to synthesize
            context_id: Context ID (auto-generated if None)
            voice_settings: Voice settings (only for first message in context)
            
        Returns:
            context_id used
        """
        if not self.websocket:
            raise Exception("WebSocket not connected. Call connect_websocket() first.")
        
        if not context_id:
            context_id = self._generate_context_id()
        
        message = {
            "text": text,
            "context_id": context_id
        }
        
        # Include voice settings only for first message in context
        if voice_settings:
            message["voice_settings"] = voice_settings
        
        await self.websocket.send(json.dumps(message))
        logging.info(f"📤 Sent text to context '{context_id}': {text[:50]}...")
        
        return context_id
    
    async def continue_context(self, text: str, context_id: str):
        """Add more text to an existing context."""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps({
            "text": text,
            "context_id": context_id
        }))
        logging.info(f"➕ Continued context '{context_id}': {text[:50]}...")
    
    async def flush_context(self, context_id: str):
        """Force generation of any buffered audio in the context."""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps({
            "context_id": context_id,
            "flush": True
        }))
        logging.info(f"🚀 Flushed context '{context_id}'")
    
    async def close_context(self, context_id: str):
        """Close a specific context (useful for interruptions)."""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps({
            "context_id": context_id,
            "close_context": True
        }))
        logging.info(f"🔒 Closed context '{context_id}'")
    
    async def keep_context_alive(self, context_id: str):
        """
        Keep a context alive by sending empty text.
        Prevents 20-second timeout during processing delays.
        """
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        await self.websocket.send(json.dumps({
            "context_id": context_id,
            "text": ""
        }))
        logging.debug(f"💓 Kept context '{context_id}' alive")
    
    async def handle_interruption(
        self, 
        old_context_id: str, 
        new_text: str,
        new_context_id: Optional[str] = None
    ) -> str:
        """
        Handle user interruption by closing current context and starting new one.
        
        Args:
            old_context_id: Context to close
            new_text: Text for new context
            new_context_id: Optional new context ID
            
        Returns:
            new_context_id used
        """
        # Close interrupted context
        await self.close_context(old_context_id)
        
        # Start new context
        new_context_id = await self.send_text_in_context(new_text, new_context_id)
        
        logging.info(f"🔄 Handled interruption: '{old_context_id}' → '{new_context_id}'")
        return new_context_id
    
    async def stream_audio_from_text(
        self, 
        text: str, 
        language: Optional[str] = None,
        websocket_client=None
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio generation using multi-context WebSocket.
        Compatible with existing ProfAI audio streaming interface.
        
        Args:
            text: Text to synthesize
            language: Language code (not used by ElevenLabs multi-context)
            websocket_client: Client WebSocket to check connection
            
        Yields:
            Audio chunks as bytes
        """
        try:
            # Connect if not already connected
            if not self.websocket:
                await self.connect_websocket()
            
            # Generate unique context
            context_id = self._generate_context_id()
            
            # Send text for synthesis
            await self.send_text_in_context(text, context_id)
            await self.flush_context(context_id)
            
            # Receive and yield audio chunks
            chunk_count = 0
            async for message in self.websocket:
                # Check if client is still connected
                if websocket_client and hasattr(websocket_client, 'closed'):
                    if websocket_client.closed:
                        logging.info("🔌 Client disconnected, stopping audio stream")
                        await self.close_context(context_id)
                        break
                
                try:
                    data = json.loads(message)
                    
                    # Check if this message is for our context
                    if data.get("contextId") != context_id:
                        continue
                    
                    # Yield audio chunk
                    if data.get("audio"):
                        chunk_count += 1
                        audio_base64 = data["audio"]
                        audio_bytes = base64.b64decode(audio_base64)
                        
                        logging.debug(f"🎵 Chunk {chunk_count}: {len(audio_bytes)} bytes")
                        yield audio_bytes
                    
                    # Check if context is complete
                    if data.get("is_final"):
                        logging.info(f"✅ Context '{context_id}' completed: {chunk_count} chunks")
                        break
                        
                except json.JSONDecodeError:
                    logging.error("Failed to parse WebSocket message")
                    continue
            
            # Close context
            await self.close_context(context_id)
            
        except ConnectionClosed as e:
            logging.warning(f"WebSocket closed during streaming: {e}")
        except Exception as e:
            logging.error(f"❌ Error in audio streaming: {e}")
            raise
    
    async def generate_audio(
        self, 
        text: str, 
        language: Optional[str] = None,
        speaker: Optional[str] = None
    ) -> bytes:
        """
        Generate complete audio (non-streaming).
        Compatible with existing ProfAI interface.
        
        Args:
            text: Text to synthesize
            language: Language code (not used)
            speaker: Speaker name (not used, voice_id used instead)
            
        Returns:
            Complete audio as bytes
        """
        audio_chunks = []
        async for chunk in self.stream_audio_from_text(text, language):
            audio_chunks.append(chunk)
        
        return b''.join(audio_chunks)
    
    async def transcribe_audio(self, audio_buffer, language: Optional[str] = None) -> str:
        """
        Transcribe audio using ElevenLabs STT.
        Note: ElevenLabs Conversational AI handles STT automatically via VAD.
        This method is for compatibility with existing interface.
        
        Args:
            audio_buffer: Audio data
            language: Language code
            
        Returns:
            Transcribed text
        """
        # ElevenLabs Conversational AI handles STT automatically
        # This is a placeholder for compatibility
        logging.warning("⚠️ ElevenLabs STT is handled automatically in Conversational AI mode")
        return ""
    
    async def translate_text(
        self, 
        text: str, 
        target_language_code: str, 
        source_language_code: str
    ) -> str:
        """
        Translate text.
        Note: ElevenLabs doesn't have translation API.
        This method is for compatibility - you may want to use another service.
        
        Args:
            text: Text to translate
            target_language_code: Target language
            source_language_code: Source language
            
        Returns:
            Translated text (or original if translation not available)
        """
        logging.warning("⚠️ ElevenLabs doesn't support translation. Returning original text.")
        return text


class ElevenLabsConversationalAgent:
    """
    High-level conversational agent using ElevenLabs.
    Handles greeting, turn-taking, and interruptions.
    """
    
    def __init__(self, greeting_text: str = None):
        self.service = ElevenLabsService()
        self.greeting_text = greeting_text or config.AGENT_GREETING
        self.current_context_id = None
        self.is_speaking = False
    
    async def start_conversation(self):
        """Start conversation with greeting."""
        await self.service.connect_websocket()
        
        # Send greeting
        self.current_context_id = await self.service.send_text_in_context(
            self.greeting_text,
            context_id="greeting"
        )
        await self.service.flush_context(self.current_context_id)
        self.is_speaking = True
        
        logging.info(f"👋 Started conversation with greeting")
    
    async def respond(self, text: str) -> str:
        """
        Respond to user input.
        
        Args:
            text: Response text
            
        Returns:
            context_id of the response
        """
        self.current_context_id = await self.service.send_text_in_context(text)
        await self.service.flush_context(self.current_context_id)
        self.is_speaking = True
        
        return self.current_context_id
    
    async def handle_user_interruption(self, new_response: str):
        """Handle user interrupting agent."""
        if self.current_context_id and self.is_speaking:
            self.current_context_id = await self.service.handle_interruption(
                self.current_context_id,
                new_response
            )
            await self.service.flush_context(self.current_context_id)
    
    async def end_conversation(self):
        """End conversation and cleanup."""
        await self.service.disconnect_websocket()
        logging.info("👋 Ended conversation")
