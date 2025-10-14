# ⚡ ElevenLabs Quick Start Guide

## 🚀 **Get Started in 5 Minutes**

### **Step 1: Get API Key (2 minutes)**
1. Go to https://elevenlabs.io
2. Sign up / Log in
3. Click your profile → **API Keys**
4. Copy your API key

### **Step 2: Set Environment Variables (1 minute)**
```bash
# Create or edit .env file
echo "ELEVENLABS_API_KEY=your_api_key_here" >> .env
echo "ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM" >> .env  # Rachel voice (default)
```

### **Step 3: Install Dependencies (1 minute)**
```bash
pip install elevenlabs websockets
```

### **Step 4: Test Backend (1 minute)**
```bash
python test_elevenlabs_integration.py
```

Expected output:
```
✅ PASSED: Basic Connection
✅ PASSED: Text-to-Speech
✅ PASSED: Audio Streaming
✅ PASSED: Context Management
✅ PASSED: Conversational Agent
🎉 All tests passed!
```

### **Step 5: Test Frontend (30 seconds)**
1. Open `websocket_tests/elevenlabs-voice-agent.html`
2. Update lines 280-281:
   ```javascript
   const ELEVENLABS_API_KEY = 'your_api_key_here';
   const VOICE_ID = '21m00Tcm4TlvDq8ikWAM';
   ```
3. Open in browser
4. Click **"Connect & Start"**
5. Agent greets you! 🎉

---

## 💻 **Basic Usage**

### **Python Backend**
```python
from services.elevenlabs_service import ElevenLabsConversationalAgent

# Create agent
agent = ElevenLabsConversationalAgent()

# Start conversation (agent greets automatically)
await agent.start_conversation()

# Respond to user
await agent.respond("I can help you with Auburn University information.")

# Handle interruption
await agent.handle_user_interruption("Let me address that...")

# End conversation
await agent.end_conversation()
```

### **JavaScript Frontend**
```javascript
// Connect to ElevenLabs
const ws = new WebSocket(
    `wss://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}/multi-stream-input?model_id=eleven_flash_v2_5`
);

// Send greeting
ws.send(JSON.stringify({
    text: "Hello! How can I help you?",
    context_id: "greeting",
    flush: true
}));

// Receive audio
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.audio) {
        playAudio(data.audio);  // Play audio chunk
    }
};
```

---

## 🎯 **Key Features**

| Feature | Status | How to Use |
|---------|--------|------------|
| **Agent Greeting** | ✅ | Automatic on connection |
| **VAD** | ✅ | Built-in, no code needed |
| **Two-way Chat** | ✅ | Automatic turn-taking |
| **Interruptions** | ✅ | `handle_interruption()` |
| **Multi-language** | ✅ | 32 languages supported |
| **Audio Streaming** | ✅ | `stream_audio_from_text()` |

---

## 🔧 **Common Commands**

```bash
# Test integration
python test_elevenlabs_integration.py

# Run WebSocket server
python run_profai_websocket.py

# Install dependencies
pip install -r requirements.txt

# Check configuration
python -c "import config; print(f'API Key: {bool(config.ELEVENLABS_API_KEY)}')"
```

---

## 📁 **Important Files**

```
services/elevenlabs_service.py          # Backend service
websocket_tests/elevenlabs-voice-agent.html  # Frontend demo
config.py                               # Configuration
test_elevenlabs_integration.py          # Test script
ELEVENLABS_IMPLEMENTATION_GUIDE.md      # Full guide
```

---

## 🐛 **Troubleshooting**

### **"WebSocket connection failed"**
```bash
# Check API key
python -c "import config; print(config.ELEVENLABS_API_KEY)"

# Test connection
python test_elevenlabs_integration.py
```

### **"No audio playing"**
```javascript
// Check browser console for errors
// Ensure user interaction before playing audio
// Check audio context is initialized
```

### **"Context timeout"**
```python
# Send keep-alive
await service.keep_context_alive(context_id)
```

---

## 💰 **Cost Calculator**

```python
# Average conversation: 2000 characters
cost_per_char = 0.00018
cost_per_conversation = 2000 * cost_per_char
# = $0.36 per conversation

# 1000 conversations/month
monthly_cost = 1000 * cost_per_conversation
# = $360/month
```

---

## 🎓 **Learn More**

- **Full Guide**: `ELEVENLABS_IMPLEMENTATION_GUIDE.md`
- **Migration Plan**: `ELEVENLABS_MIGRATION_PLAN.md`
- **Summary**: `ELEVENLABS_SUMMARY.md`
- **ElevenLabs Docs**: https://elevenlabs.io/docs

---

## ✅ **Checklist**

- [ ] Get ElevenLabs API key
- [ ] Set environment variables
- [ ] Install dependencies
- [ ] Run test script
- [ ] Test frontend demo
- [ ] Integrate with backend
- [ ] Deploy to production

---

## 🎉 **You're Ready!**

Everything is set up. Just add your API key and start testing!

**Questions?** Check the full implementation guide.
**Issues?** Run the test script to diagnose.
**Ready?** Open the HTML demo and click "Connect & Start"!
