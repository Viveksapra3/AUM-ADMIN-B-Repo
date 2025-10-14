# 🎙️ Production Audio WebSocket - Complete Guide

## 🎯 **What You Now Have**

A **production-ready full-duplex audio streaming system** with:

✅ **Speech-to-Text** (32+ languages via ElevenLabs)  
✅ **Text-to-Speech** (ElevenLabs voices)  
✅ **Custom Fine-Tuned LLM** (GPT-4.1-mini: `ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T`)  
✅ **Voice Activity Detection** (automatic turn-taking)  
✅ **Multi-language Support** (16 languages in UI, 32+ supported)  
✅ **Real-time Audio Streaming** (browser ↔ server ↔ ElevenLabs)  
✅ **Secure Architecture** (API keys on server)  

---

## 📁 **Files Created**

### **Backend:**
1. ✅ **`services/elevenlabs_conversational_service.py`** - Core service (300+ lines)
2. ✅ **`run_audio_server.py`** - Production WebSocket server (250+ lines)

### **Frontend:**
3. ✅ **`websocket_tests/audio-client.html`** - Full audio client (500+ lines)

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                         BROWSER                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Microphone  │→ │ Web Audio API │→ │  WebSocket   │      │
│  └─────────────┘  └──────────────┘  └──────┬───────┘      │
│                                              │               │
└──────────────────────────────────────────────┼──────────────┘
                                               │
                                               │ Audio (PCM16)
                                               │ + JSON Messages
                                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    YOUR SERVER (Port 8766)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  run_audio_server.py                                 │  │
│  │  - Handles client connections                        │  │
│  │  - Routes audio/messages                             │  │
│  │  - Manages conversations                             │  │
│  └────────────┬─────────────────────────┬─────────────┘  │
│               │                          │                  │
└───────────────┼──────────────────────────┼──────────────────┘
                │                          │
                │ Audio + Text             │ Text (User Query)
                ▼                          ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│   ELEVENLABS API        │    │   OPENAI API            │
│                         │    │                         │
│  - Speech-to-Text       │    │  Custom Fine-Tuned LLM  │
│  - Text-to-Speech       │    │  Model: AUM Counselor   │
│  - Voice Activity Det.  │    │                         │
│  - 32+ Languages        │    │  ft:gpt-4.1-mini...     │
│                         │    │                         │
└─────────────────────────┘    └─────────────────────────┘
```

---

## 🚀 **Quick Start (Local Testing)**

### **Step 1: Install Dependencies**

```bash
cd /Users/amarprakash/Desktop/AUM-ADMIN-B-Repo/Prof_AI

# Activate virtual environment
source venv/bin/activate

# Install (if not already installed)
pip install websockets openai elevenlabs
```

### **Step 2: Configure Environment Variables**

Edit `.env` file:

```bash
# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_flash_v2_5

# OpenAI (for custom LLM)
OPENAI_API_KEY=your_openai_api_key

# Server
HOST=0.0.0.0
```

### **Step 3: Start the Server**

**Terminal 1:**
```bash
python run_audio_server.py
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════╗
║        🎙️  AUM Audio WebSocket Server  🎙️                    ║
║  Server: ws://0.0.0.0:8766                                  ║
║  Features:                                                   ║
║  ✅ Full-duplex audio streaming                             ║
║  ✅ Speech-to-Text (32+ languages)                          ║
║  ✅ Text-to-Speech (ElevenLabs)                             ║
║  ✅ Custom LLM (GPT-4.1-mini fine-tuned)                    ║
╚══════════════════════════════════════════════════════════════╝

✅ Server running on ws://0.0.0.0:8766
📝 Waiting for client connections...
```

### **Step 4: Start HTTP Server**

**Terminal 2:**
```bash
cd websocket_tests
python3 -m http.server 8000
```

### **Step 5: Open Client**

**Browser:**
```
http://localhost:8000/audio-client.html
```

1. Select language
2. Click "Start Conversation"
3. Allow microphone access
4. Start speaking!

---

## 🌍 **Supported Languages**

The system supports **32+ languages**:

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en` | English | `es` | Spanish |
| `fr` | French | `de` | German |
| `it` | Italian | `pt` | Portuguese |
| `pl` | Polish | `tr` | Turkish |
| `ru` | Russian | `nl` | Dutch |
| `cs` | Czech | `ar` | Arabic |
| `zh` | Chinese | `ja` | Japanese |
| `ko` | Korean | `hi` | Hindi |

And many more...

---

## 🔧 **How It Works**

### **1. Connection Flow**

```
Browser → Server: "start_conversation" (with language)
Server → ElevenLabs: Connect to Conversational AI
ElevenLabs → Server: conversation_id
Server → Browser: "conversation_started"
```

### **2. Audio Flow (User Speaking)**

```
Browser Microphone → PCM16 Audio
Browser → Server: Audio chunks (base64)
Server → ElevenLabs: Audio chunks
ElevenLabs → Server: User transcript (STT)
Server → Custom LLM: User message
Custom LLM → Server: AI response
Server → ElevenLabs: AI response text
ElevenLabs → Server: Audio (TTS)
Server → Browser: Audio chunks
Browser → Speakers: Play audio
```

### **3. Message Types**

**Client → Server:**
- `start_conversation` - Start new conversation
- `audio` - Audio chunk (user speaking)
- `text` - Text input (optional)
- `change_language` - Change language
- `disconnect` - End conversation

**Server → Client:**
- `connection_ready` - Connected to server
- `conversation_started` - ElevenLabs ready
- `audio` - Audio chunk (agent speaking)
- `user_transcript` - User's speech transcribed
- `agent_response` - Agent's text response

---

## 🤖 **Custom LLM Integration**

Your fine-tuned model is automatically used:

```python
# In elevenlabs_conversational_service.py
self.custom_model = "ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T"

# Called automatically when user speaks
response = self.openai_client.chat.completions.create(
    model=self.custom_model,
    messages=conversation_history,
    temperature=0.7,
    max_tokens=500
)
```

**Conversation History Maintained:**
- System prompt (agent greeting)
- All previous user messages
- All previous agent responses
- Current user message

---

## 🌐 **Production Deployment**

### **Option 1: VPS/Cloud Server**

1. **Deploy to server** (AWS, DigitalOcean, etc.)

```bash
# On server
git clone your-repo
cd Prof_AI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
nano .env

# Run with process manager
pm2 start run_audio_server.py --interpreter python3
# Or use systemd, supervisor, etc.
```

2. **Configure domain/SSL:**

```nginx
# Nginx config
server {
    listen 443 ssl;
    server_name voice.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8766;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

3. **Update client URL:**

```javascript
// In audio-client.html
const SERVER_URL = 'wss://voice.yourdomain.com';
```

### **Option 2: Docker**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8766

CMD ["python", "run_audio_server.py"]
```

```bash
# Build and run
docker build -t aum-voice-agent .
docker run -p 8766:8766 --env-file .env aum-voice-agent
```

---

## 📊 **Testing**

### **Test Audio Streaming:**

```bash
# Terminal 1
python run_audio_server.py

# Terminal 2
cd websocket_tests
python3 -m http.server 8000

# Browser
open http://localhost:8000/audio-client.html
```

### **Test Different Languages:**

1. Select language from dropdown
2. Click "Start Conversation"
3. Speak in selected language
4. Agent responds in same language

---

## 🐛 **Troubleshooting**

### **Issue: No audio playback**

```javascript
// Check browser console for errors
// Ensure HTTPS (required for microphone)
// Check audio permissions
```

### **Issue: Microphone not working**

```bash
# Browser must be HTTPS or localhost
# Check browser permissions
# Test microphone: chrome://settings/content/microphone
```

### **Issue: Connection fails**

```bash
# Check server is running
lsof -i :8766

# Check firewall
sudo ufw allow 8766

# Check logs
tail -f server.log
```

### **Issue: LLM not responding**

```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Check model name
# Verify: ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T

# Test API
curl https://api.openai.com/v1/models/ft:gpt-4.1-mini-2025-04-14:professor-ai:aum:COPCJu5T \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 📈 **Performance Optimization**

### **1. Audio Quality:**

```python
# In elevenlabs_conversational_service.py
"optimize_streaming_latency": 3,  # 0-4 (4 = lowest latency)
"stability": 0.5,  # 0-1 (voice consistency)
"similarity_boost": 0.75,  # 0-1 (voice similarity)
```

### **2. LLM Response Time:**

```python
# Reduce max_tokens for faster responses
max_tokens=300  # Instead of 500

# Adjust temperature
temperature=0.5  # More deterministic, faster
```

### **3. Audio Buffering:**

```javascript
// In audio-client.html
const processor = audioContext.createScriptProcessor(
    2048,  // Smaller buffer = lower latency (try 2048, 4096, 8192)
    1, 1
);
```

---

## 🎯 **Key Features**

| Feature | Status | Details |
|---------|--------|---------|
| **STT** | ✅ | ElevenLabs (32+ languages) |
| **TTS** | ✅ | ElevenLabs (natural voices) |
| **VAD** | ✅ | Automatic (built-in) |
| **Custom LLM** | ✅ | GPT-4.1-mini fine-tuned |
| **Multi-language** | ✅ | 32+ languages |
| **Real-time** | ✅ | Full-duplex streaming |
| **Secure** | ✅ | API keys on server |
| **Production** | ✅ | Ready to deploy |

---

## 📝 **Summary**

You now have a **complete production-ready voice agent**:

✅ **Backend**: `run_audio_server.py` (runs on port 8766)  
✅ **Frontend**: `audio-client.html` (connects to server)  
✅ **Service**: Full ElevenLabs Conversational AI integration  
✅ **LLM**: Your custom fine-tuned model  
✅ **Languages**: 32+ supported  
✅ **Deployment**: Ready for production server  

**To use:**
1. Start server: `python run_audio_server.py`
2. Open client: `http://localhost:8000/audio-client.html`
3. Select language and start speaking!

🚀 **Ready to deploy to production!**
