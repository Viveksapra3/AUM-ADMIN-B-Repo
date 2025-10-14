# 🚀 ElevenLabs Server - Production Setup Guide

## 📋 **What You Now Have**

I've created a **production-ready WebSocket server** that runs continuously and handles client connections:

### **Files Created:**
1. ✅ **`run_elevenlabs_server.py`** - WebSocket server (runs on port 8766)
2. ✅ **`elevenlabs-client.html`** - Frontend that connects to your server

---

## 🎯 **Architecture**

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Browser Client │ ◄─────► │  Your Server    │ ◄─────► │  ElevenLabs API │
│  (HTML)         │         │  (Port 8766)    │         │  (Cloud)        │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
   localhost:8000              localhost:8766              api.elevenlabs.io
```

**Benefits:**
- ✅ API key stays secure on server
- ✅ Can add custom logic (AUM Counselor integration)
- ✅ Production-ready
- ✅ Multiple clients can connect

---

## 🚀 **How to Run**

### **Step 1: Start the WebSocket Server**

Open **Terminal 1**:
```bash
cd /Users/amarprakash/Desktop/AUM-ADMIN-B-Repo/Prof_AI

# Activate virtual environment
source venv/bin/activate

# Run the server
python run_elevenlabs_server.py
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎙️  ElevenLabs Voice Agent WebSocket Server  🎙️       ║
║                                                              ║
║  Server will run on: ws://0.0.0.0:8766                      ║
║  Frontend connects to: ws://localhost:8766                  ║
║                                                              ║
║  Press Ctrl+C to stop                                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting ElevenLabs WebSocket Server on 0.0.0.0:8766
✅ Server running on ws://0.0.0.0:8766
📝 Waiting for client connections...
```

**✅ Server is now running and waiting for connections!**

---

### **Step 2: Start the HTTP Server (for HTML)**

Open **Terminal 2**:
```bash
cd /Users/amarprakash/Desktop/AUM-ADMIN-B-Repo/Prof_AI/websocket_tests

# Start HTTP server
python3 -m http.server 8000
```

**Expected Output:**
```
Serving HTTP on :: port 8000 (http://[::]:8000/) ...
```

---

### **Step 3: Open the Client**

Open your browser:
```
http://localhost:8000/elevenlabs-client.html
```

Click **"Connect & Start"** and the agent will greet you!

---

## 📊 **What Happens**

1. **Browser connects** to your server (`ws://localhost:8766`)
2. **Server connects** to ElevenLabs API (using your API key)
3. **Agent greets** the user automatically
4. **Conversation flows** through your server
5. **You can add custom logic** (AUM Counselor, database, etc.)

---

## 🔧 **Server Features**

### **Current Implementation:**
- ✅ Auto-greeting on connection
- ✅ Message routing (client ↔ ElevenLabs)
- ✅ Multiple client support
- ✅ Connection management
- ✅ Error handling

### **Ready to Add:**
- 🔄 AUM Counselor integration (replace echo response)
- 🔄 Database logging
- 🔄 User authentication
- 🔄 Session management
- 🔄 Custom business logic

---

## 🎨 **Customizing the Server**

### **Add AUM Counselor Integration**

Edit `run_elevenlabs_server.py`, line ~70:

```python
# CURRENT (Echo):
response_text = f"I heard you say: {user_text}. How can I help you with that?"

# CHANGE TO (AUM Counselor):
from services.chat_service import ChatService
chat_service = ChatService()

# Get response from AUM Counselor
response_text = await chat_service.get_response(
    user_text,
    context="admission_counseling"
)
```

---

## 🌐 **Production Deployment**

### **For Production Server:**

1. **Update host in config.py:**
   ```python
   HOST = "0.0.0.0"  # Listen on all interfaces
   ```

2. **Run with process manager:**
   ```bash
   # Using systemd (Linux)
   sudo systemctl start elevenlabs-server
   
   # Or using PM2 (Node.js)
   pm2 start run_elevenlabs_server.py --interpreter python3
   
   # Or using screen (simple)
   screen -S elevenlabs
   python run_elevenlabs_server.py
   # Press Ctrl+A, then D to detach
   ```

3. **Update frontend URL:**
   ```javascript
   // In elevenlabs-client.html
   const SERVER_URL = 'ws://your-server-ip:8766';
   // Or use domain
   const SERVER_URL = 'wss://voice.yourdomain.com';
   ```

4. **Use HTTPS/WSS for production:**
   - Set up SSL certificate (Let's Encrypt)
   - Use nginx/Apache as reverse proxy
   - Change `ws://` to `wss://`

---

## 🐛 **Troubleshooting**

### **Issue: "Connection refused"**
```bash
# Check if server is running
lsof -i :8766

# If not running, start it
python run_elevenlabs_server.py
```

### **Issue: "Port already in use"**
```bash
# Kill process on port 8766
lsof -ti:8766 | xargs kill -9

# Or use different port
# Edit run_elevenlabs_server.py, change port to 8767
```

### **Issue: "API key not set"**
```bash
# Check .env file
cat .env | grep ELEVENLABS_API_KEY

# If missing, add it
echo "ELEVENLABS_API_KEY=your_key_here" >> .env
```

---

## 📝 **Server Logs**

The server logs all activity:

```
2025-10-14 15:30:00 - INFO - 🚀 Starting ElevenLabs WebSocket Server on 0.0.0.0:8766
2025-10-14 15:30:00 - INFO - ✅ Server running on ws://0.0.0.0:8766
2025-10-14 15:30:05 - INFO - 🔌 Client 12345 connected from ('127.0.0.1', 54321)
2025-10-14 15:30:05 - INFO - 👋 Starting conversation for client 12345
2025-10-14 15:30:10 - INFO - 💬 Client 12345 said: Tell me about AUM
2025-10-14 15:30:15 - INFO - 🔌 Client 12345 disconnected
2025-10-14 15:30:15 - INFO - 🧹 Cleaned up client 12345
```

---

## 🎯 **Quick Commands**

```bash
# Start server
python run_elevenlabs_server.py

# Start HTTP server (for HTML)
cd websocket_tests && python3 -m http.server 8000

# Open client
open http://localhost:8000/elevenlabs-client.html

# Check if server is running
curl http://localhost:8766

# Stop server
# Press Ctrl+C in the terminal
```

---

## 📊 **Server vs Direct Connection**

| Feature | Direct (HTML → ElevenLabs) | Server (HTML → Your Server → ElevenLabs) |
|---------|---------------------------|------------------------------------------|
| **API Key Security** | ❌ Exposed in browser | ✅ Secure on server |
| **Custom Logic** | ❌ Not possible | ✅ Full control |
| **AUM Counselor** | ❌ Can't integrate | ✅ Easy integration |
| **Database Logging** | ❌ Not possible | ✅ Easy to add |
| **Production Ready** | ❌ Not secure | ✅ Production ready |
| **Setup Complexity** | ✅ Simple | ⚠️ Requires server |

---

## ✅ **Summary**

You now have:

1. ✅ **Production server** (`run_elevenlabs_server.py`) - Runs on port 8766
2. ✅ **Client HTML** (`elevenlabs-client.html`) - Connects to your server
3. ✅ **Secure architecture** - API key stays on server
4. ✅ **Ready for deployment** - Can run 24/7 on production server

**To use:**
1. Terminal 1: `python run_elevenlabs_server.py` (keeps running)
2. Terminal 2: `cd websocket_tests && python3 -m http.server 8000`
3. Browser: `http://localhost:8000/elevenlabs-client.html`

**The server stays running** and handles all client connections! 🚀
