# 🎙️ AUM Voice Agent - Complete System

> **Production-ready voice agent with continuous microphone, VAD, multi-language support, and avatar integration**

---

## 🚀 **Quick Start (One Command)**

```bash
./start_voice_agent.sh
```

That's it! The script will:
- ✅ Start WebSocket server (port 8766)
- ✅ Start HTTP server (port 8000)
- ✅ Open avatar client in browser
- ✅ Everything ready to use!

---

## 📋 **What You Get**

### **Core Features:**
- ✅ **Continuous Microphone** - Always listening
- ✅ **Voice Activity Detection (VAD)** - Automatic speech detection
- ✅ **Speech-to-Text** - Whisper API (95+ languages)
- ✅ **Custom LLM** - Your fine-tuned GPT-4.1-mini model
- ✅ **Text-to-Speech** - ElevenLabs natural voices
- ✅ **Multi-Language** - 11 languages in UI, 95+ supported
- ✅ **Avatar Events** - For lip-sync and animations
- ✅ **Concurrent Users** - Unlimited simultaneous connections

---

## 📁 **Project Structure**

```
Prof_AI/
├── run_simple_audio_server.py          # Main WebSocket server
├── start_voice_agent.sh                # Quick start script
├── services/
│   └── elevenlabs_direct_service.py    # Core service (STT, TTS, LLM)
├── websocket_tests/
│   ├── avatar-audio-client.html        # Voice + VAD client ⭐
│   └── simple-audio-client.html        # Text-only client
└── docs/
    ├── FINAL_IMPLEMENTATION_SUMMARY.md # Complete overview
    ├── AVATAR_INTEGRATION_GUIDE.md     # Avatar integration
    ├── SIMPLE_AUDIO_QUICKSTART.md      # Quick start guide
    └── PRODUCTION_AUDIO_GUIDE.md       # Production deployment
```

---

## 🎯 **Three Ways to Use**

### **1. One-Command Start (Easiest)**
```bash
./start_voice_agent.sh
```

### **2. Manual Start**
```bash
# Terminal 1: WebSocket Server
python run_simple_audio_server.py

# Terminal 2: HTTP Server
cd websocket_tests && python3 -m http.server 8000

# Browser
open http://localhost:8000/avatar-audio-client.html
```

### **3. Production Deployment**
```bash
# Using PM2
pm2 start run_simple_audio_server.py --interpreter python3 --name aum-voice

# Using Docker
docker-compose up -d
```

---

## 🎭 **Client Options**

### **Avatar Client (Recommended for Avatar Integration)**
**File:** `avatar-audio-client.html`

**Features:**
- ✅ Continuous microphone
- ✅ Voice Activity Detection
- ✅ Avatar events for lip-sync
- ✅ Multi-language support
- ✅ Real-time VAD indicator

**URL:** `http://localhost:8000/avatar-audio-client.html`

---

### **Simple Client (Text Input)**
**File:** `simple-audio-client.html`

**Features:**
- ✅ Text input
- ✅ Audio output
- ✅ No microphone needed
- ✅ Good for testing

**URL:** `http://localhost:8000/simple-audio-client.html`

---

## 🌍 **Supported Languages**

| Language | Code | STT | TTS |
|----------|------|-----|-----|
| English | `en` | ✅ | ✅ |
| Spanish | `es` | ✅ | ✅ |
| French | `fr` | ✅ | ✅ |
| German | `de` | ✅ | ✅ |
| Italian | `it` | ✅ | ✅ |
| Portuguese | `pt` | ✅ | ✅ |
| Hindi | `hi` | ✅ | ✅ |
| Chinese | `zh` | ✅ | ✅ |
| Japanese | `ja` | ✅ | ✅ |
| Korean | `ko` | ✅ | ✅ |
| Arabic | `ar` | ✅ | ✅ |

**Plus 84+ more via Whisper!**

---

## 🎭 **Avatar Integration**

### **Listen to Events:**

```javascript
window.addEventListener('avatarEvent', (e) => {
    switch(e.detail.type) {
        case 'user_speaking_start':
            avatar.startListening();
            break;
        case 'agent_speaking_start':
            avatar.startSpeaking();
            break;
        case 'audio_chunk':
            avatar.syncLips(e.detail.audioBuffer);
            break;
    }
});
```

### **Available Events:**
- `session_started` - Voice session began
- `user_speaking_start` - User started speaking
- `user_speaking_end` - User stopped speaking
- `user_transcript` - User's speech transcribed
- `agent_response` - Agent's text response
- `agent_speaking_start` - Agent starts speaking
- `audio_chunk` - Audio data for lip-sync
- `agent_speaking_end` - Agent finished speaking
- `session_ended` - Voice session ended

**See:** `AVATAR_INTEGRATION_GUIDE.md` for complete examples

---

## 🔧 **Configuration**

### **VAD Settings (in `avatar-audio-client.html`):**

```javascript
const VAD_THRESHOLD = 0.01;           // Speech detection sensitivity
const VAD_SILENCE_DURATION = 1500;    // Silence duration (ms)
```

**Adjust for your needs:**
- Lower threshold = more sensitive
- Higher silence duration = more complete sentences

---

### **Environment Variables (`.env`):**

```bash
# Required
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENAI_API_KEY=your_openai_key

# Optional
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_flash_v2_5
HOST=0.0.0.0
```

---

## 📊 **Architecture**

```
Browser (Mic) → VAD → WebSocket → Server
                                     ↓
                              Whisper STT
                                     ↓
                              Your Custom LLM
                                     ↓
                              ElevenLabs TTS
                                     ↓
Browser (Speakers) ← WebSocket ← Server
```

---

## 💰 **Cost Estimate**

**Per 1000 users (5 min each):**
- Whisper STT: ~$30
- Your LLM: ~$0.50
- ElevenLabs TTS: ~$10-50
- **Total: ~$40-80**

Very affordable for production!

---

## 🚀 **Production Deployment**

### **Option 1: PM2 (Recommended)**

```bash
pm2 start run_simple_audio_server.py --interpreter python3 --name aum-voice
pm2 startup
pm2 save
```

### **Option 2: Docker**

```bash
docker build -t aum-voice .
docker run -d -p 8766:8766 --env-file .env aum-voice
```

### **Option 3: Systemd**

See `PRODUCTION_AUDIO_GUIDE.md` for complete setup.

---

## 🐛 **Troubleshooting**

### **Server won't start:**
```bash
# Kill existing processes
lsof -ti:8766 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Restart
./start_voice_agent.sh
```

### **Microphone not working:**
- Use HTTPS or localhost
- Check browser permissions
- Test: `chrome://settings/content/microphone`

### **VAD too sensitive:**
```javascript
// In avatar-audio-client.html
const VAD_THRESHOLD = 0.02; // Increase
```

### **Speech gets cut off:**
```javascript
const VAD_SILENCE_DURATION = 2000; // Increase
```

---

## 📚 **Documentation**

- **`FINAL_IMPLEMENTATION_SUMMARY.md`** - Complete overview
- **`AVATAR_INTEGRATION_GUIDE.md`** - Avatar integration guide
- **`SIMPLE_AUDIO_QUICKSTART.md`** - Quick start guide
- **`PRODUCTION_AUDIO_GUIDE.md`** - Production deployment

---

## ✅ **Testing Checklist**

- [ ] Server starts without errors
- [ ] Client connects successfully
- [ ] Microphone access granted
- [ ] VAD detects speech
- [ ] Audio transcribed correctly
- [ ] LLM responds appropriately
- [ ] Audio plays back
- [ ] Avatar events fire correctly
- [ ] Multi-language works
- [ ] Concurrent users work

---

## 🎊 **You're Ready!**

### **To Start:**
```bash
./start_voice_agent.sh
```

### **To Test:**
1. Open `http://localhost:8000/avatar-audio-client.html`
2. Click "Start Voice Session"
3. Allow microphone
4. Start speaking!

### **To Deploy:**
```bash
pm2 start run_simple_audio_server.py --interpreter python3
```

---

## 📞 **Support**

Check the documentation files for detailed guides:
- Avatar integration → `AVATAR_INTEGRATION_GUIDE.md`
- Production setup → `PRODUCTION_AUDIO_GUIDE.md`
- Quick start → `SIMPLE_AUDIO_QUICKSTART.md`

---

## 🎉 **Features Summary**

✅ Continuous microphone with VAD  
✅ Multi-language support (95+ languages)  
✅ Your custom fine-tuned LLM  
✅ Natural voice responses  
✅ Avatar-ready events  
✅ Concurrent user support  
✅ Production deployment ready  
✅ One-command start  
✅ Complete documentation  

**Everything you need for a production voice agent!** 🚀
