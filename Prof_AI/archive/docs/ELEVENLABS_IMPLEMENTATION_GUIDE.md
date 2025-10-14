# 🎙️ ElevenLabs Implementation Guide

## ✅ **What Has Been Implemented**

I've created a complete ElevenLabs integration with Multi-Context WebSocket and VAD support for your ProfAI system. Here's what's ready:

### **1. Backend Service** (`services/elevenlabs_service.py`)
- ✅ Multi-Context WebSocket connection
- ✅ Context management (create, continue, flush, close)
- ✅ Interruption handling
- ✅ Audio streaming compatible with existing interface
- ✅ Keep-alive mechanism for long processing
- ✅ High-level conversational agent class

### **2. Configuration** (`config.py`)
- ✅ ElevenLabs API key configuration
- ✅ Voice ID and model settings
- ✅ Agent greeting message
- ✅ All settings via environment variables

### **3. Frontend Demo** (`websocket_tests/elevenlabs-voice-agent.html`)
- ✅ Beautiful, modern UI
- ✅ Auto-connect and greeting
- ✅ VAD visualization
- ✅ Conversation history
- ✅ Multi-language selector
- ✅ Mute/unmute controls
- ✅ Real-time status indicators

### **4. Documentation**
- ✅ Migration plan (`ELEVENLABS_MIGRATION_PLAN.md`)
- ✅ This implementation guide
- ✅ Inline code documentation

---

## 🚀 **Quick Start**

### **Step 1: Get ElevenLabs API Key**

1. Go to [ElevenLabs](https://elevenlabs.io)
2. Sign up / Log in
3. Go to **Profile** → **API Keys**
4. Copy your API key

### **Step 2: Choose or Create a Voice**

1. Go to **Voices** in ElevenLabs dashboard
2. Either:
   - **Use existing voice**: Copy the Voice ID
   - **Clone a voice**: Upload samples and get Voice ID
   - **Use default**: Rachel voice ID: `21m00Tcm4TlvDq8ikWAM`

### **Step 3: Set Environment Variables**

Create or update your `.env` file:

```bash
# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here
ELEVENLABS_MODEL=eleven_flash_v2_5

# Optional: For Agents Platform
ELEVENLABS_AGENT_ID=your_agent_id_here
```

### **Step 4: Install Dependencies**

```bash
pip install elevenlabs websockets
```

### **Step 5: Test the Service**

```python
import asyncio
from services.elevenlabs_service import ElevenLabsConversationalAgent

async def test():
    agent = ElevenLabsConversationalAgent()
    await agent.start_conversation()
    # Agent will greet automatically
    await asyncio.sleep(5)
    await agent.end_conversation()

asyncio.run(test())
```

### **Step 6: Open Frontend Demo**

1. Update API key in `websocket_tests/elevenlabs-voice-agent.html`:
   ```javascript
   const ELEVENLABS_API_KEY = 'your_api_key_here';
   const VOICE_ID = 'your_voice_id_here';
   ```

2. Open the HTML file in your browser
3. Click "Connect & Start"
4. Agent will greet you automatically!

---

## 🎯 **Integration Options**

### **Option A: Direct Browser Connection (Recommended for Testing)**

**Pros**: Simple, fast, no backend needed
**Cons**: API key exposed in browser (use signed URLs for production)

```javascript
// Client connects directly to ElevenLabs
const ws = new WebSocket(
    `wss://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}/multi-stream-input?model_id=${MODEL_ID}`
);
```

### **Option B: Proxy Through ProfAI Backend (Production)**

**Pros**: Secure, full control, custom logic
**Cons**: Additional latency, more complex

```python
# Your WebSocket server proxies to ElevenLabs
async def handle_client(client_ws):
    elevenlabs_ws = await elevenlabs_service.connect_websocket()
    
    # Forward messages between client and ElevenLabs
    async def forward_to_elevenlabs():
        async for msg in client_ws:
            await elevenlabs_ws.send(msg)
    
    async def forward_to_client():
        async for msg in elevenlabs_ws:
            await client_ws.send(msg)
    
    await asyncio.gather(
        forward_to_elevenlabs(),
        forward_to_client()
    )
```

### **Option C: ElevenLabs Agents Platform (Easiest)**

**Pros**: Fully managed, built-in VAD, no code needed
**Cons**: Monthly subscription, less customization

```javascript
// Use ElevenLabs SDK
import { Conversation } from "@elevenlabs/react";

<Conversation agentId="your_agent_id" />
```

---

## 🔄 **Replacing Sarvam with ElevenLabs**

### **Update Audio Service**

```python
# services/audio_service.py

from services.elevenlabs_service import ElevenLabsService

class AudioService:
    def __init__(self):
        # OLD: self.sarvam_service = SarvamService()
        # NEW:
        self.elevenlabs_service = ElevenLabsService()
    
    async def stream_audio_from_text(self, text, language=None, websocket=None):
        # OLD: return self.sarvam_service.stream_audio_generation(...)
        # NEW:
        async for chunk in self.elevenlabs_service.stream_audio_from_text(
            text, language, websocket
        ):
            yield chunk
```

### **Update WebSocket Server for Greeting**

```python
# websocket_server.py

async def websocket_handler(websocket, path=None):
    # ... existing code ...
    
    # Send connection ready
    await websocket.send({
        "type": "connection_ready",
        "message": "ProfAI WebSocket connected",
        "client_id": client_id
    })
    
    # NEW: Send agent greeting automatically
    await websocket.send({
        "type": "agent_greeting",
        "text": config.AGENT_GREETING
    })
    
    # Start audio for greeting
    async for audio_chunk in audio_service.stream_audio_from_text(
        config.AGENT_GREETING
    ):
        await websocket.send({
            "type": "audio_chunk",
            "audio_data": base64.b64encode(audio_chunk).decode('utf-8')
        })
```

---

## 🎨 **Frontend Integration**

### **React Example**

```jsx
import { useConversation } from "@elevenlabs/react";

function VoiceAgent() {
    const conversation = useConversation({
        onConnect: () => console.log("Connected!"),
        onDisconnect: () => console.log("Disconnected"),
        onMessage: (message) => console.log("Message:", message),
        onError: (error) => console.error("Error:", error)
    });

    return (
        <div>
            <button onClick={() => conversation.startSession({
                agentId: "your_agent_id"
            })}>
                Start Conversation
            </button>
            
            <button onClick={() => conversation.endSession()}>
                End Conversation
            </button>
            
            <div>
                Status: {conversation.status}
            </div>
        </div>
    );
}
```

### **Vanilla JavaScript Example**

See `websocket_tests/elevenlabs-voice-agent.html` for complete implementation.

---

## 🌍 **Multi-Language Support**

### **Supported Languages**

ElevenLabs supports 32 languages:

```javascript
const LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'pl': 'Polish',
    'tr': 'Turkish',
    'ru': 'Russian',
    'nl': 'Dutch',
    'cs': 'Czech',
    'ar': 'Arabic',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'hi': 'Hindi',
    // ... and 16 more
};
```

### **Language Selection**

```python
# Backend
await elevenlabs_service.send_text_in_context(
    text="Bonjour! Comment puis-je vous aider?",
    context_id="greeting_fr"
)
```

```javascript
// Frontend
const languageSelect = document.getElementById('languageSelect');
const selectedLanguage = languageSelect.value;

// ElevenLabs automatically detects language from text
// Or specify in agent configuration
```

---

## 🎙️ **VAD (Voice Activity Detection)**

### **How It Works**

ElevenLabs Conversational AI has **built-in VAD**:

1. **Automatic Detection**: No manual implementation needed
2. **Turn-Taking**: Automatically detects when user starts/stops speaking
3. **Interruption Handling**: Stops agent when user speaks
4. **Silence Detection**: Knows when user is done speaking

### **VAD Visualization (Frontend)**

```javascript
// Visualize VAD activity
function animateVAD(active) {
    const bars = document.querySelectorAll('.vad-bar');
    bars.forEach(bar => {
        if (active) {
            bar.style.height = Math.random() * 60 + 20 + 'px';
        } else {
            bar.style.height = '10px';
        }
    });
}

// Update based on agent state
websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.audio) {
        animateVAD(true); // Agent speaking
    }
    
    if (data.is_final) {
        animateVAD(false); // Agent finished
    }
};
```

---

## 🔧 **Advanced Features**

### **1. Interruption Handling**

```python
# When user interrupts
old_context = "agent_speaking_123"
new_response = "Sorry, let me address that..."

new_context = await elevenlabs_service.handle_interruption(
    old_context_id=old_context,
    new_text=new_response
)
```

### **2. Context Management**

```python
# Create context
context_id = await elevenlabs_service.send_text_in_context(
    "Hello! How can I help you?",
    context_id="greeting"
)

# Add more to same context
await elevenlabs_service.continue_context(
    "I'm here to answer your questions.",
    context_id="greeting"
)

# Flush (force generation)
await elevenlabs_service.flush_context("greeting")

# Close context
await elevenlabs_service.close_context("greeting")
```

### **3. Keep Context Alive**

```python
# During long processing (prevents 20s timeout)
await elevenlabs_service.keep_context_alive(context_id)
```

### **4. Voice Settings**

```python
# Customize voice (only on first message in context)
voice_settings = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.5,
    "use_speaker_boost": True
}

await elevenlabs_service.send_text_in_context(
    text="Hello!",
    context_id="greeting",
    voice_settings=voice_settings
)
```

---

## 📊 **Performance Optimization**

### **1. Use Fast Model**

```python
# config.py
ELEVENLABS_MODEL = "eleven_flash_v2_5"  # Fastest, lowest latency
```

### **2. Stream in Chunks**

```python
# Stream long responses in sentences
sentences = text.split('. ')
for sentence in sentences:
    await elevenlabs_service.continue_context(sentence + '. ', context_id)
    await elevenlabs_service.flush_context(context_id)  # Flush each sentence
```

### **3. Optimize Audio Format**

```python
# Use MP3 for smaller size (default)
# Or PCM for lower latency (larger size)
```

### **4. Connection Pooling**

```python
# Reuse WebSocket connection
# Don't reconnect for each message
```

---

## 🐛 **Troubleshooting**

### **Issue 1: "WebSocket connection failed"**

**Solution**:
- Check API key is correct
- Verify voice ID exists
- Check network/firewall settings

### **Issue 2: "No audio playing"**

**Solution**:
```javascript
// Ensure audio context is initialized
audioContext = new (window.AudioContext || window.webkitAudioContext)();

// Check browser autoplay policy
// User interaction required before playing audio
```

### **Issue 3: "Context timeout after 20 seconds"**

**Solution**:
```python
# Send keep-alive messages
await elevenlabs_service.keep_context_alive(context_id)

# Or increase timeout (up to 180s)
# Add ?inactivity_timeout=180 to WebSocket URL
```

### **Issue 4: "API key exposed in browser"**

**Solution**:
```python
# Use signed URLs (production)
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
signed_url = client.conversational_ai.get_signed_url(agent_id=AGENT_ID)

# Send signed_url to frontend
# Frontend connects using signed URL (no API key needed)
```

---

## 💰 **Cost Estimation**

### **Pricing (as of 2025)**

- **TTS**: ~$0.00018 per character (Flash model)
- **Conversational AI**: Included in TTS pricing
- **Agents Platform**: $99/month + usage

### **Example Calculation**

```
Average conversation:
- Agent greeting: 100 characters
- 10 exchanges: 200 characters each = 2000 characters
- Total: 2100 characters

Cost per conversation: 2100 * $0.00018 = $0.378
Cost for 1000 conversations: $378

With Agents Platform: $99/month + $378 = $477/month
```

---

## 🎯 **Next Steps**

1. ✅ **Test the demo** - Open `elevenlabs-voice-agent.html`
2. ✅ **Get API key** - Sign up at elevenlabs.io
3. ✅ **Choose integration** - Direct, Proxy, or Agents Platform
4. ✅ **Update backend** - Replace Sarvam calls with ElevenLabs
5. ✅ **Test thoroughly** - Verify all features work
6. ✅ **Deploy** - Use signed URLs for production

---

## 📚 **Resources**

- [ElevenLabs Docs](https://elevenlabs.io/docs)
- [Multi-Context WebSocket](https://elevenlabs.io/docs/conversational-ai/client-sdk/multi-context-websocket)
- [Agents Platform](https://elevenlabs.io/docs/agents-platform/overview)
- [Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [React SDK](https://github.com/elevenlabs/elevenlabs-react)

---

## ✅ **Summary**

You now have:

1. ✅ Complete ElevenLabs service implementation
2. ✅ Multi-Context WebSocket support
3. ✅ Built-in VAD (no manual implementation)
4. ✅ Agent greeting on connection
5. ✅ Two-way conversation support
6. ✅ Multi-language support (32 languages)
7. ✅ Beautiful frontend demo
8. ✅ Interruption handling
9. ✅ Full documentation

**Ready to test!** Just add your API key and voice ID, then open the HTML file! 🚀
