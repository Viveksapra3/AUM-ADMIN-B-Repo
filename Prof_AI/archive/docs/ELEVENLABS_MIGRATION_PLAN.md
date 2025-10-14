# 🎙️ ElevenLabs Migration Plan - Multi-Context WebSocket with VAD

## 📋 **Migration Overview**

**Goal**: Replace Sarvam AI with ElevenLabs Conversational AI using Multi-Context WebSocket with built-in VAD (Voice Activity Detection) for natural two-way conversations.

**Key Changes**:
1. ✅ **Agent initiates conversation** with greeting on page load
2. ✅ **Built-in VAD** - No manual implementation needed (ElevenLabs handles it)
3. ✅ **Two-way conversation** - Natural turn-taking
4. ✅ **Multi-language support** - 32 languages supported by ElevenLabs
5. ✅ **Keep existing functionality** - Course generation, chat, teaching modes

---

## 🌍 **Supported Languages (ElevenLabs)**

ElevenLabs supports **32 languages** including:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Polish (pl)
- Turkish (tr)
- Russian (ru)
- Dutch (nl)
- Czech (cs)
- Arabic (ar)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Hindi (hi)
- And 16 more...

**Note**: More comprehensive than Sarvam's 11 Indian languages, but loses some regional Indian language support.

---

## 🏗️ **Architecture Changes**

### **Current Architecture (Sarvam)**
```
Client WebSocket (Port 8766)
    ↓
ProfAI WebSocket Server
    ↓
Chat Service → AUM Counselor → OpenAI LLM
    ↓
Sarvam Service (TTS/STT/Translation)
    ↓
Audio Streaming to Client
```

### **New Architecture (ElevenLabs)**
```
Client Browser
    ↓
ElevenLabs Conversational AI WebSocket (Direct)
    ├── Built-in VAD (Voice Activity Detection)
    ├── Built-in STT (Speech-to-Text)
    ├── Built-in TTS (Text-to-Speech)
    └── LLM Integration (OpenAI/Custom)
    ↓
[Optional] ProfAI Backend for:
    - Course Management
    - Document Processing
    - Custom Business Logic
```

---

## 🎯 **Implementation Strategy**

### **Option 1: Full ElevenLabs Agents Platform (RECOMMENDED)**
**Pros**:
- ✅ Built-in VAD - No implementation needed
- ✅ Automatic turn-taking
- ✅ Agent greeting on connection
- ✅ Interruption handling
- ✅ Multi-language support
- ✅ Managed infrastructure

**Cons**:
- ❌ Less control over conversation flow
- ❌ Requires ElevenLabs Agents Platform subscription
- ❌ Custom LLM integration more complex

### **Option 2: Multi-Context WebSocket + Custom VAD**
**Pros**:
- ✅ Full control over conversation
- ✅ Custom LLM (AUM Counselor)
- ✅ Flexible architecture

**Cons**:
- ❌ Need to implement VAD manually
- ❌ More complex implementation
- ❌ Need to handle turn-taking logic

---

## 📦 **Required Changes**

### **1. New Dependencies**
```bash
# Remove Sarvam
pip uninstall sarvamai

# Add ElevenLabs
pip install elevenlabs websockets
```

### **2. New Configuration**
```python
# config.py additions
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "default_voice")
ELEVENLABS_MODEL = "eleven_flash_v2_5"  # Fast, low-latency
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")  # For Agents Platform

# Greeting message
AGENT_GREETING = "Hello! I'm Alex from Auburn University at Montgomery. How can I help you today?"
```

### **3. New Service: ElevenLabsService**
```python
services/elevenlabs_service.py
    - Multi-Context WebSocket connection
    - TTS streaming
    - STT transcription
    - Context management (interruptions)
```

### **4. Modified Files**
- `services/audio_service.py` - Replace Sarvam with ElevenLabs
- `services/chat_service.py` - Update for ElevenLabs integration
- `websocket_server.py` - Add agent greeting on connection
- `config.py` - Add ElevenLabs configuration
- `requirements.txt` - Update dependencies

### **5. New Frontend**
```html
websocket_tests/elevenlabs-voice-agent.html
    - Direct ElevenLabs WebSocket connection
    - Auto-start conversation with greeting
    - VAD visualization
    - Multi-language selector
```

---

## 🔄 **Conversation Flow**

### **New Flow with ElevenLabs**
```
1. User opens page
   ↓
2. WebSocket connects to ElevenLabs
   ↓
3. Agent speaks greeting automatically
   "Hello! I'm Alex from Auburn University at Montgomery..."
   ↓
4. VAD listens for user speech (automatic)
   ↓
5. User speaks (VAD detects start/end automatically)
   ↓
6. ElevenLabs STT → Text
   ↓
7. Send to AUM Counselor LLM
   ↓
8. LLM Response → ElevenLabs TTS
   ↓
9. Agent speaks response
   ↓
10. VAD listens again (loop continues)
```

### **Interruption Handling**
```
Agent speaking...
   ↓
User starts speaking (VAD detects)
   ↓
Close current context (stop agent)
   ↓
Create new context for user input
   ↓
Process user input
   ↓
Agent responds in new context
```

---

## 🎨 **Frontend Implementation**

### **Key Features**
1. **Auto-connect on page load**
2. **Agent greeting plays automatically**
3. **Visual VAD indicator** (listening/speaking states)
4. **Language selector**
5. **Mute/unmute microphone**
6. **Conversation history display**

### **WebSocket Events**
```javascript
// Connect
ws.connect(agent_id, {
    onConnect: () => {
        // Agent starts speaking greeting automatically
    },
    onMessage: (message) => {
        // Display agent response
    },
    onAudio: (audioChunk) => {
        // Play audio
    },
    onUserSpeaking: () => {
        // Show "listening" indicator
    },
    onAgentSpeaking: () => {
        // Show "speaking" indicator
    }
});
```

---

## 🔧 **Backend Integration**

### **Option A: Direct ElevenLabs (Simpler)**
```
Client Browser
    ↓
ElevenLabs WebSocket (Direct)
    ↓
ElevenLabs Agent with Custom LLM
    ↓
Your Backend API (for LLM responses)
```

### **Option B: Proxy Through ProfAI (More Control)**
```
Client Browser
    ↓
ProfAI WebSocket Server
    ↓
ElevenLabs Multi-Context WebSocket
    ↓
AUM Counselor Service
```

---

## 📝 **Implementation Steps**

### **Phase 1: Setup (Day 1)**
- [ ] Create ElevenLabs account
- [ ] Get API key
- [ ] Create/clone voice
- [ ] Set up agent (if using Agents Platform)
- [ ] Install dependencies

### **Phase 2: Backend (Day 2-3)**
- [ ] Create `elevenlabs_service.py`
- [ ] Update `audio_service.py`
- [ ] Modify `websocket_server.py` for greeting
- [ ] Update `config.py`
- [ ] Test multi-context WebSocket

### **Phase 3: Frontend (Day 4)**
- [ ] Create new HTML interface
- [ ] Implement WebSocket connection
- [ ] Add VAD visualization
- [ ] Add language selector
- [ ] Test auto-greeting

### **Phase 4: Integration (Day 5)**
- [ ] Connect frontend to backend
- [ ] Test two-way conversation
- [ ] Test interruptions
- [ ] Test multi-language
- [ ] Performance optimization

### **Phase 5: Testing & Deployment (Day 6-7)**
- [ ] End-to-end testing
- [ ] Load testing
- [ ] Bug fixes
- [ ] Documentation
- [ ] Deployment

---

## ⚠️ **Migration Risks & Mitigation**

### **Risk 1: Loss of Indian Language Support**
- **Impact**: Sarvam supports 11 Indian languages, ElevenLabs has limited support
- **Mitigation**: 
  - Keep Sarvam as fallback for unsupported languages
  - Use ElevenLabs for English, Hindi, and major languages
  - Implement language detection and routing

### **Risk 2: Cost Increase**
- **Impact**: ElevenLabs may be more expensive than Sarvam
- **Mitigation**:
  - Use `eleven_flash_v2_5` model (fastest, cheapest)
  - Implement usage monitoring
  - Set up cost alerts

### **Risk 3: Latency**
- **Impact**: Additional network hop if proxying through backend
- **Mitigation**:
  - Use direct client-to-ElevenLabs connection (Option A)
  - Use WebSocket compression
  - Optimize audio chunk size

### **Risk 4: Existing Functionality**
- **Impact**: Course generation, document processing may break
- **Mitigation**:
  - Keep existing backend services intact
  - Only replace audio/conversation layer
  - Maintain backward compatibility

---

## 💰 **Cost Comparison**

### **Sarvam AI**
- TTS: ~$0.0001 per character
- STT: ~$0.0001 per second
- Translation: ~$0.0001 per character

### **ElevenLabs**
- TTS: ~$0.00018 per character (Flash model)
- STT: Included in Conversational AI
- Agents Platform: $99/month + usage

**Recommendation**: Start with Multi-Context WebSocket (no subscription) for testing.

---

## 🎯 **Success Criteria**

1. ✅ Agent greets user automatically on page load
2. ✅ VAD detects user speech without button press
3. ✅ Natural two-way conversation
4. ✅ Interruptions handled gracefully
5. ✅ Multi-language support working
6. ✅ Sub-500ms latency for first audio chunk
7. ✅ Existing course/document features still work
8. ✅ No regression in AUM counselor responses

---

## 📚 **Resources**

- [ElevenLabs Multi-Context WebSocket Docs](https://elevenlabs.io/docs/conversational-ai/client-sdk/multi-context-websocket)
- [ElevenLabs Agents Platform](https://elevenlabs.io/docs/agents-platform/overview)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [Voice Activity Detection (VAD)](https://elevenlabs.io/docs/conversational-ai/features/vad)

---

## 🚀 **Next Steps**

1. **Review this plan** and confirm approach (Option A vs Option B)
2. **Get ElevenLabs API key** and set up account
3. **Start with Phase 1** - Setup and testing
4. **Implement incrementally** - Test each phase before moving forward
5. **Keep Sarvam as fallback** during migration

---

**Ready to proceed? Let me know which option you prefer and I'll start implementing!**
