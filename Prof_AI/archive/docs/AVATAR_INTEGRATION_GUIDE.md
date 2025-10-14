# 🎭 Avatar Integration Guide - Continuous Microphone + VAD

## ✅ What You Now Have

A **complete avatar-ready voice system** with:

- ✅ **Continuous Microphone** - Always listening
- ✅ **Voice Activity Detection (VAD)** - Detects when user speaks
- ✅ **Speech-to-Text** - Whisper API (95+ languages)
- ✅ **Custom LLM** - Your fine-tuned model
- ✅ **Text-to-Speech** - ElevenLabs voices
- ✅ **Avatar Events** - For lip-sync and animations
- ✅ **Multi-language Support** - 11 languages in UI, 95+ supported

---

## 📁 Files Created

1. ✅ **`websocket_tests/avatar-audio-client.html`** - Avatar-ready client with VAD
2. ✅ **Updated `services/elevenlabs_direct_service.py`** - Added Whisper transcription
3. ✅ **Updated `run_simple_audio_server.py`** - Handles audio transcription

---

## 🎯 How It Works

### **Flow:**

```
1. User starts voice session
   ↓
2. Microphone continuously captures audio
   ↓
3. VAD detects speech (RMS > threshold)
   ↓
4. Collects audio while speaking
   ↓
5. Detects silence (1.5s) → End of speech
   ↓
6. Sends audio to server
   ↓
7. Server transcribes (Whisper API)
   ↓
8. Your Custom LLM generates response
   ↓
9. ElevenLabs converts to speech
   ↓
10. Audio plays + Avatar speaks (lip-sync)
```

---

## 🚀 Quick Start

### **Step 1: Start Server**

```bash
cd /Users/amarprakash/Desktop/AUM-ADMIN-B-Repo/Prof_AI
source venv/bin/activate
python run_simple_audio_server.py
```

### **Step 2: Open Avatar Client**

```
http://localhost:8000/avatar-audio-client.html
```

### **Step 3: Test VAD**

1. Select language
2. Click "Start Voice Session"
3. Allow microphone
4. **Start speaking** - VAD will detect automatically!
5. Watch the VAD indicator light up
6. Stop speaking - after 1.5s silence, it processes
7. Get audio response!

---

## 🎭 Avatar Integration

### **Avatar Events**

The client emits custom events you can listen to:

```javascript
window.addEventListener('avatarEvent', (e) => {
    console.log('Avatar Event:', e.detail);
    
    switch(e.detail.type) {
        case 'session_started':
            // Initialize avatar
            break;
            
        case 'user_speaking_start':
            // Show "listening" animation
            avatar.startListening();
            break;
            
        case 'user_speaking_end':
            // Show "processing" animation
            avatar.showProcessing();
            break;
            
        case 'user_transcript':
            // Display user's text (optional)
            console.log('User said:', e.detail.text);
            break;
            
        case 'agent_response':
            // Agent's text response
            console.log('Agent responds:', e.detail.text);
            break;
            
        case 'agent_speaking_start':
            // Start lip-sync animation
            avatar.startSpeaking();
            break;
            
        case 'audio_chunk':
            // Use audio data for lip-sync
            const audioBuffer = e.detail.audioBuffer;
            avatar.syncLips(audioBuffer);
            break;
            
        case 'agent_speaking_end':
            // Return to idle
            avatar.stopSpeaking();
            break;
            
        case 'session_ended':
            // Cleanup
            avatar.reset();
            break;
    }
});
```

---

## 🎙️ VAD Configuration

### **Adjust Sensitivity:**

In `avatar-audio-client.html`:

```javascript
const VAD_THRESHOLD = 0.01; // Adjust this
// Lower = more sensitive (0.001 - 0.1)
// 0.001 = very sensitive (picks up whispers)
// 0.1 = less sensitive (only loud speech)

const VAD_SILENCE_DURATION = 1500; // ms
// How long to wait after silence before processing
// 1000 = 1 second (faster, may cut off)
// 2000 = 2 seconds (slower, more complete)
```

---

## 🌍 Multi-Language Support

### **Supported Languages:**

| Code | Language | Whisper Support |
|------|----------|-----------------|
| `en` | English | ✅ Excellent |
| `es` | Spanish | ✅ Excellent |
| `fr` | French | ✅ Excellent |
| `de` | German | ✅ Excellent |
| `it` | Italian | ✅ Excellent |
| `pt` | Portuguese | ✅ Excellent |
| `hi` | Hindi | ✅ Excellent |
| `zh` | Chinese | ✅ Excellent |
| `ja` | Japanese | ✅ Excellent |
| `ko` | Korean | ✅ Excellent |
| `ar` | Arabic | ✅ Excellent |

**Total:** 95+ languages supported by Whisper!

---

## 🎨 Avatar Animation States

### **Recommended States:**

1. **Idle** - Default state, subtle breathing animation
2. **Listening** - User is speaking, avatar shows attention
3. **Processing** - Thinking animation (optional)
4. **Speaking** - Lip-sync with audio, gestures
5. **Error** - Error state (optional)

### **Example Integration:**

```javascript
class AvatarController {
    constructor() {
        this.state = 'idle';
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        window.addEventListener('avatarEvent', (e) => {
            this.handleEvent(e.detail);
        });
    }
    
    handleEvent(event) {
        switch(event.type) {
            case 'user_speaking_start':
                this.setState('listening');
                break;
                
            case 'user_speaking_end':
                this.setState('processing');
                break;
                
            case 'agent_speaking_start':
                this.setState('speaking');
                break;
                
            case 'agent_speaking_end':
                this.setState('idle');
                break;
                
            case 'audio_chunk':
                this.updateLipSync(event.audioBuffer);
                break;
        }
    }
    
    setState(newState) {
        this.state = newState;
        // Update avatar animation
        console.log('Avatar state:', newState);
    }
    
    updateLipSync(audioBuffer) {
        // Analyze audio for lip-sync
        // Use audio amplitude to control mouth opening
        const data = audioBuffer.getChannelData(0);
        let sum = 0;
        for (let i = 0; i < data.length; i++) {
            sum += Math.abs(data[i]);
        }
        const amplitude = sum / data.length;
        const mouthOpening = amplitude * 100; // 0-100%
        
        // Apply to avatar
        console.log('Mouth opening:', mouthOpening + '%');
    }
}

// Initialize
const avatar = new AvatarController();
```

---

## 🔧 Advanced Configuration

### **1. Improve VAD Accuracy:**

```javascript
// In avatar-audio-client.html
processor.onaudioprocess = (e) => {
    const inputData = e.inputBuffer.getChannelData(0);
    
    // Calculate RMS
    let sum = 0;
    for (let i = 0; i < inputData.length; i++) {
        sum += inputData[i] * inputData[i];
    }
    const rms = Math.sqrt(sum / inputData.length);
    
    // Apply smoothing (optional)
    const smoothedRMS = (rms * 0.3) + (previousRMS * 0.7);
    
    // Use smoothed value for VAD
    if (smoothedRMS > VAD_THRESHOLD) {
        // Speech detected
    }
};
```

### **2. Add Noise Gate:**

```javascript
const NOISE_GATE = 0.005; // Minimum level to consider

if (rms < NOISE_GATE) {
    // Ignore (background noise)
    return;
}
```

### **3. Add Pre-roll Buffer:**

```javascript
// Keep last 500ms of audio before speech detection
const preRollBuffer = [];
const PRE_ROLL_DURATION = 500; // ms

// When speech detected, include pre-roll
if (!isSpeaking) {
    audioChunks = [...preRollBuffer]; // Include pre-roll
}
```

---

## 📊 Performance Optimization

### **1. Reduce Latency:**

```javascript
// Smaller buffer = lower latency
const processor = audioContext.createScriptProcessor(
    2048, // Try 2048, 4096, or 8192
    1, 1
);
```

### **2. Optimize Audio Quality:**

```javascript
// Balance quality vs. file size
mediaStream = await navigator.mediaDevices.getUserMedia({ 
    audio: {
        sampleRate: 16000, // Whisper optimal
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
    } 
});
```

### **3. Batch Audio Chunks:**

```javascript
// Send audio every N chunks instead of continuously
const BATCH_SIZE = 5;
if (audioChunks.length >= BATCH_SIZE) {
    sendAudioForTranscription();
}
```

---

## 🎯 Integration Checklist

- [ ] **Start server** - `python run_simple_audio_server.py`
- [ ] **Open avatar client** - `http://localhost:8000/avatar-audio-client.html`
- [ ] **Test VAD** - Speak and watch detection
- [ ] **Add avatar events listener** - Copy event handler code
- [ ] **Implement avatar states** - Idle, listening, speaking
- [ ] **Add lip-sync** - Use audio buffer data
- [ ] **Test multi-language** - Switch languages
- [ ] **Optimize VAD** - Adjust threshold and silence duration
- [ ] **Deploy** - Move to production server

---

## 🌐 Production Deployment

### **Same as before:**

```bash
# On server
pm2 start run_simple_audio_server.py --interpreter python3

# Or with systemd
sudo systemctl start aum-voice-agent
```

### **Update client URL:**

```javascript
// In avatar-audio-client.html
const SERVER_URL = 'wss://your-domain.com';
```

---

## 🐛 Troubleshooting

### **Issue: VAD too sensitive**

```javascript
// Increase threshold
const VAD_THRESHOLD = 0.02; // Higher = less sensitive
```

### **Issue: Speech gets cut off**

```javascript
// Increase silence duration
const VAD_SILENCE_DURATION = 2000; // 2 seconds
```

### **Issue: Background noise triggers VAD**

```javascript
// Add noise gate
const NOISE_GATE = 0.005;
if (rms < NOISE_GATE) return;
```

### **Issue: Microphone not working**

- Ensure HTTPS or localhost
- Check browser permissions
- Test: `chrome://settings/content/microphone`

---

## 📈 Cost Considerations

### **Whisper API Pricing:**

- **$0.006 per minute** of audio
- Example: 1000 users, 5 min each = $30/day
- Much cheaper than ElevenLabs STT

### **ElevenLabs TTS Pricing:**

- Varies by plan
- Consider caching common responses

---

## 🎊 Summary

You now have:

✅ **Continuous microphone** - Always listening  
✅ **Voice Activity Detection** - Automatic speech detection  
✅ **Multi-language STT** - Whisper API (95+ languages)  
✅ **Custom LLM** - Your fine-tuned model  
✅ **Audio responses** - ElevenLabs TTS  
✅ **Avatar events** - Ready for lip-sync  
✅ **Production-ready** - Deploy now!  

**Perfect for avatar integration!** 🎭🚀

---

## 📝 Quick Commands

```bash
# Start server
python run_simple_audio_server.py

# Open avatar client
open http://localhost:8000/avatar-audio-client.html

# Test VAD
# Just speak - it detects automatically!
```

**Your avatar-ready voice system is complete!** 🎉
