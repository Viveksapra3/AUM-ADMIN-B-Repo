"""
ElevenLabs Conversational AI Service
Full-duplex audio streaming with STT, TTS, and custom LLM integration
"""

import asyncio
import json
import base64
import logging
from typing import Optional, Callable
import websockets
from websockets.exceptions import ConnectionClosed
import config
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

class ElevenLabsConversationalService:
    """
    Production-ready ElevenLabs Conversational AI service.
    Handles audio streaming, STT, TTS, and custom LLM integration.
    """
    
    def __init__(self, 
                 agent_id: Optional[str] = None,
                 voice_id: Optional[str] = None,
                 custom_llm_callback: Optional[Callable] = None):
        """
        Initialize the conversational service.
        
        Args:
            agent_id: ElevenLabs agent ID (optional, for pre-configured agents)
            voice_id: Voice ID to use
            custom_llm_callback: Async function to call your custom LLM
        """
        self.api_key = config.ELEVENLABS_API_KEY
        self.agent_id = agent_id
        self.voice_id = voice_id or config.ELEVENLABS_VOICE_ID
        self.custom_llm_callback = custom_llm_callback
        self.websocket = None
        self.conversation_id = None
        
        # OpenAI client for custom LLM
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.custom_model = "ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T"
        
        logging.info("✅ ElevenLabs Conversational Service initialized")
    
    async def connect(self, language: str = "en") -> str:
        """
        Connect to ElevenLabs Conversational AI WebSocket.
        
        Args:
            language: Language code (en, es, fr, de, etc.)
            
        Returns:
            conversation_id
        """
        url = "wss://api.elevenlabs.io/v1/convai/conversation"
        
        # Query parameters
        params = {
            "agent_id": self.agent_id if self.agent_id else "",
        }
        
        # Build URL with params
        query_string = "&".join([f"{k}={v}" for k, v in params.items() if v])
        if query_string:
            url = f"{url}?{query_string}"
        
        try:
            self.websocket = await websockets.connect(
                url,
                additional_headers={
                    "xi-api-key": self.api_key
                },
                max_size=16 * 1024 * 1024,  # 16MB
                ping_interval=30,
                ping_timeout=20
            )
            
            # Send initial configuration
            config_message = {
                "type": "conversation_initiation_client_data",
                "conversation_config_override": {
                    "agent": {
                        "prompt": {
                            "prompt": config.AGENT_GREETING
                        },
                        "first_message": config.AGENT_GREETING,
                        "language": language
                    },
                    "tts": {
                        "voice_id": self.voice_id,
                        "model_id": config.ELEVENLABS_MODEL,
                        "optimize_streaming_latency": 3,
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
            }
            
            await self.websocket.send(json.dumps(config_message))
            logging.info(f"✅ Connected to ElevenLabs Conversational AI (Language: {language})")
            
            # Wait for conversation_id
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") == "conversation_initiation_metadata":
                        self.conversation_id = data.get("conversation_id")
                        logging.info(f"📝 Conversation ID: {self.conversation_id}")
                        return self.conversation_id
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            logging.error(f"❌ Failed to connect: {e}")
            raise
    
    async def send_audio(self, audio_chunk: bytes):
        """
        Send audio chunk to ElevenLabs (user speaking).
        
        Args:
            audio_chunk: Raw audio bytes (PCM16, 16kHz, mono)
        """
        if not self.websocket:
            raise Exception("Not connected. Call connect() first.")
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_chunk).decode('utf-8')
        
        message = {
            "type": "audio",
            "audio": audio_base64
        }
        
        await self.websocket.send(json.dumps(message))
    
    async def send_text(self, text: str):
        """
        Send text input (instead of audio).
        
        Args:
            text: User text input
        """
        if not self.websocket:
            raise Exception("Not connected. Call connect() first.")
        
        message = {
            "type": "user_transcript",
            "user_transcript": text
        }
        
        await self.websocket.send(json.dumps(message))
        logging.info(f"📤 Sent user text: {text}")
    
    async def get_llm_response(self, user_message: str, conversation_history: list) -> str:
        """
        Get response from custom fine-tuned LLM.
        
        Args:
            user_message: User's message
            conversation_history: List of previous messages
            
        Returns:
            LLM response text
        """
        try:
            # Build messages for custom LLM
            messages = [
                {"role": "system", "content": config.AGENT_GREETING}
            ]
            
            # Add conversation history
            messages.extend(conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call custom fine-tuned model
            response = self.openai_client.chat.completions.create(
                model=self.custom_model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            llm_response = response.choices[0].message.content
            logging.info(f"🤖 LLM Response: {llm_response[:100]}...")
            
            return llm_response
            
        except Exception as e:
            logging.error(f"❌ LLM error: {e}")
            return "I apologize, but I'm having trouble processing your request. Could you please try again?"
    
    async def handle_messages(self, 
                            on_audio: Callable,
                            on_transcript: Callable,
                            on_agent_response: Callable):
        """
        Handle incoming messages from ElevenLabs.
        
        Args:
            on_audio: Callback for audio chunks (agent speaking)
            on_transcript: Callback for user transcripts (STT result)
            on_agent_response: Callback for agent responses
        """
        if not self.websocket:
            raise Exception("Not connected. Call connect() first.")
        
        conversation_history = []
        
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    if message_type == "audio":
                        # Agent speaking - audio chunk
                        audio_base64 = data.get("audio")
                        if audio_base64:
                            audio_bytes = base64.b64decode(audio_base64)
                            await on_audio(audio_bytes)
                    
                    elif message_type == "user_transcript":
                        # User's speech transcribed
                        transcript = data.get("user_transcript", "")
                        logging.info(f"👤 User said: {transcript}")
                        
                        # Add to history
                        conversation_history.append({
                            "role": "user",
                            "content": transcript
                        })
                        
                        await on_transcript(transcript)
                        
                        # Get response from custom LLM
                        llm_response = await self.get_llm_response(
                            transcript,
                            conversation_history
                        )
                        
                        # Add LLM response to history
                        conversation_history.append({
                            "role": "assistant",
                            "content": llm_response
                        })
                        
                        # Send LLM response back to ElevenLabs for TTS
                        await self.send_agent_response(llm_response)
                        await on_agent_response(llm_response)
                    
                    elif message_type == "agent_response":
                        # Agent's response text
                        response = data.get("agent_response", "")
                        logging.info(f"🤖 Agent: {response}")
                        await on_agent_response(response)
                    
                    elif message_type == "interruption":
                        # User interrupted agent
                        logging.info("🔄 User interrupted")
                    
                    elif message_type == "ping":
                        # Keep-alive ping
                        await self.websocket.send(json.dumps({"type": "pong"}))
                    
                except json.JSONDecodeError:
                    # Might be binary audio data
                    if isinstance(message, bytes):
                        await on_audio(message)
                    
        except ConnectionClosed:
            logging.info("🔌 Connection closed")
        except Exception as e:
            logging.error(f"❌ Error handling messages: {e}")
            raise
    
    async def send_agent_response(self, text: str):
        """
        Send agent response text for TTS.
        
        Args:
            text: Agent response text
        """
        if not self.websocket:
            raise Exception("Not connected")
        
        message = {
            "type": "agent_response",
            "agent_response": text
        }
        
        await self.websocket.send(json.dumps(message))
        logging.info(f"📤 Sent agent response for TTS")
    
    async def disconnect(self):
        """Disconnect from ElevenLabs."""
        if self.websocket:
            try:
                await self.websocket.close()
                logging.info("👋 Disconnected from ElevenLabs")
            except:
                pass
            self.websocket = None
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.websocket:
            try:
                asyncio.create_task(self.disconnect())
            except:
                pass
