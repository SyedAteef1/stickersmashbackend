# 🤖 How to Start ML Backend

## Quick Start (Simple Method)

### Step 1: Install Python Dependencies

```bash
cd mlmodel
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
python start_server.py
```

That's it! Server will start on `http://localhost:8000`

## Alternative Method (If start_server.py has issues)

```bash
cd mlmodel
python main.py
```

Or:

```bash
cd mlmodel
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## What You'll See

```
Starting SmashSticker ML Backend...
ML Features:
   - Real-time usage tracking
   - Behavioral pattern analysis
   - Usage prediction algorithms
   - Personalized recommendations
   - Break time optimization
   - Anomaly detection

✅ All dependencies are installed
Environment setup complete
Initializing ML models...
ML models initialized successfully
Server starting on http://localhost:8000
WebSocket endpoint: ws://localhost:8000/ws
API docs: http://localhost:8000/docs

Connect your SmashSticker app to start receiving ML insights!
Press Ctrl+C to stop the server
```

## Test the Connection

Open browser and go to:
```
http://localhost:8000/docs
```

You should see FastAPI documentation with all endpoints!

## In Your React Native App

The app will automatically connect to:
- **Emulator**: `http://10.0.2.2:8000`
- **Physical Device**: `http://YOUR_COMPUTER_IP:8000`

## Troubleshooting

### "Module not found" errors

```bash
pip install -r requirements.txt
```

### Port 8000 already in use

Kill the process:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux  
lsof -ti:8000 | xargs kill
```

### Can't connect from device

1. Make sure phone and computer are on **same WiFi**
2. Find your computer's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
3. Update `mlService.ts` with your IP

### MongoDB errors

**No MongoDB needed!** We use in-memory database (`database_simple.py`).

Just start the server - it works without MongoDB!

## Features Available

✅ `/api/usage` - Log usage data  
✅ `/api/predictions/{user_id}` - Get predictions  
✅ `/api/insights/{user_id}` - Get behavioral insights  
✅ `/api/recommendations/{user_id}` - Get recommendations  
✅ `/api/break-optimization` - Optimize break timing  
✅ `/ws` - WebSocket for real-time updates  

## Summary

1. Install deps: `pip install -r requirements.txt`
2. Start server: `python start_server.py`
3. That's it! 🎉

Your ML backend is now running!

