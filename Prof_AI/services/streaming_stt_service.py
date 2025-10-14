"""
Streaming STT Service with server-side endpointing (VAD via provider)

Provider: AssemblyAI (websocket)
- Multilingual support and automatic language detection when enabled on the account.
- Sends base64-encoded PCM16 16kHz mono chunks.

This service is optional. It activates only if ASSEMBLYAI_API_KEY is present.
"""
import asyncio
import base64
import json
import logging
from typing import AsyncGenerator, Optional

import websockets

import config

logger = logging.getLogger(__name__)


class StreamingSTTService:
    """
    Manages a single streaming STT session over a websocket connection to the
    provider. Exposes an async API to send audio chunks and yields partial/final
    transcripts.
    """

    def __init__(self, sample_rate: int = 16000, language_hint: Optional[str] = None):
        self.sample_rate = sample_rate
        self.language_hint = language_hint
        self.api_key = getattr(config, "ASSEMBLYAI_API_KEY", None)
        self.ws = None
        self._recv_task: Optional[asyncio.Task] = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._closed = False

    @property
    def enabled(self) -> bool:
        # Temporarily disable while we fix the new Universal Streaming API endpoint
        return False  # AssemblyAI moved to SDK-based streaming, raw WebSocket needs different endpoint

    async def start(self) -> bool:
        """Open the provider websocket and start a background receiver."""
        if not self.enabled:
            logger.warning("Streaming STT disabled: missing ASSEMBLYAI_API_KEY")
            return False

        # Use new Universal Streaming endpoint (streaming.assemblyai.com)
        url = f"wss://streaming.assemblyai.com/v2/streaming?sample_rate={self.sample_rate}&encoding=pcm_s16le"

        try:
            self.ws = await websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=10,
                max_size=16 * 1024 * 1024,
                additional_headers={
                    "Authorization": self.api_key
                }
            )
            logger.info("✅ Connected to AssemblyAI Realtime STT")

            # Optionally send a config message (if supported) for language hints.
            # Some providers accept language hints; if not supported, this is ignored.
            if self.language_hint and self.ws:
                try:
                    await self.ws.send(json.dumps({
                        "config": {
                            "language_code": self.language_hint
                        }
                    }))
                except Exception:
                    pass

            # Start background receiver
            self._recv_task = asyncio.create_task(self._receiver())
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start streaming STT: {e}")
            return False

    async def _receiver(self):
        """Receive partial/final transcripts and push to queue."""
        assert self.ws is not None
        try:
            async for msg in self.ws:
                try:
                    data = json.loads(msg)
                except Exception:
                    continue

                # Universal Streaming API returns different message format
                message_type = data.get("type")
                
                if message_type == "turn":
                    # Turn event contains transcript and end_of_turn flag
                    text = data.get("transcript", "")
                    end_of_turn = data.get("end_of_turn", False)
                    lang = data.get("language")
                    
                    if text:
                        if end_of_turn:
                            await self._queue.put({"type": "final", "text": text, "language": lang})
                        else:
                            await self._queue.put({"type": "partial", "text": text, "language": lang})
                elif message_type == "begin":
                    logger.info(f"✅ AssemblyAI session started: {data.get('id')}")
                elif message_type == "error":
                    logger.error(f"❌ AssemblyAI error: {data.get('error')}")
                else:
                    # Unknown message_type; log for debugging
                    logger.debug(f"📨 AssemblyAI message: {data}")
        except Exception as e:
            if not self._closed:
                logger.error(f"❌ STT receiver error: {e}")
        finally:
            await self._queue.put({"type": "closed"})

    async def recv(self) -> AsyncGenerator[dict, None]:
        """Yield events from the STT provider (partial/final)."""
        while True:
            event = await self._queue.get()
            if event.get("type") == "closed":
                break
            yield event

    async def send_audio_chunk(self, pcm16_bytes: bytes):
        """Send base64 PCM16 audio chunk to provider."""
        if not self.ws:
            return
        try:
            # Universal Streaming API expects raw binary audio data, not JSON
            await self.ws.send(pcm16_bytes)
        except Exception as e:
            logger.error(f"❌ Failed sending audio chunk: {e}")
            # Notify listeners and close to prevent repeated errors
            try:
                await self._queue.put({"type": "closed"})
            except Exception:
                pass
            try:
                await self.close()
            except Exception:
                pass

    async def finish(self):
        """Signal end of stream (some providers auto-detect end when socket closes)."""
        # AssemblyAI finalizes on close; nothing to send here.
        pass

    async def close(self):
        self._closed = True
        try:
            if self.ws:
                await self.ws.close()
        except Exception:
            pass
        if self._recv_task:
            try:
                await asyncio.wait_for(self._recv_task, timeout=2)
            except Exception:
                pass
        self.ws = None
        self._recv_task = None
