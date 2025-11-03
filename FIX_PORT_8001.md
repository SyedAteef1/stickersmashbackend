# Port 8001 Connection Fix

## ✅ Issues Found & Fixed

### 1. **Port Mismatch** - FIXED
- React Native app was pointing to port **8000**
- ML server is running on port **8001**
- **Fixed**: Updated `mlService.ts` to use port 8001

### 2. **Network IP Not Accessible** - NEEDS FIREWALL FIX
- Server works on `localhost:8001` ✓
- Server NOT accessible on `10.54.50.182:8001` ✗
- **Cause**: Windows Firewall blocking port 8001

## 🔧 Quick Fixes

### Fix 1: Update React Native App (DONE)
The port has been updated in the code. Just rebuild:
```bash
cd d:\work\StickerSmash
npx expo run:android
```

### Fix 2: Allow Port 8001 in Windows Firewall

**Option A: Using Command Prompt (Run as Administrator)**
```cmd
netsh advfirewall firewall add rule name="ML Server Port 8001" dir=in action=allow protocol=TCP localport=8001
```

**Option B: Using Windows Firewall GUI**
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules" → "New Rule"
4. Select "Port" → Next
5. Select "TCP" and enter "8001" → Next
6. Select "Allow the connection" → Next
7. Check all profiles → Next
8. Name it "ML Server 8001" → Finish

### Fix 3: Verify Server is Accessible
```bash
cd d:\work\mlmodel
python test_connection.py
```

## 📊 Current Status

| Test | Status | Response Time |
|------|--------|---------------|
| Localhost (127.0.0.1:8001) | ✅ Working | 2.07s |
| API Endpoint | ✅ Working | 3.66s |
| Network IP (10.54.50.182:8001) | ❌ Blocked | Timeout |

## 🚀 Complete Setup Steps

### 1. Start ML Server
```bash
cd d:\work\mlmodel
python start_server.py
```

### 2. Open Firewall Port
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="ML Server Port 8001" dir=in action=allow protocol=TCP localport=8001
```

### 3. Test Connection
```bash
python test_connection.py
```

### 4. Rebuild React Native App
```bash
cd d:\work\StickerSmash
npx expo run:android
```

## 🔍 Troubleshooting

### Server Not Responding
```bash
# Check if port is in use
netstat -ano | findstr :8001

# Kill process if needed
taskkill /PID <PID> /F

# Restart server
python start_server.py
```

### Slow Response Times
The server takes 3-5 seconds because:
- MongoDB connection timeout (2 seconds)
- Gemini API calls (1-3 seconds)
- This is normal for first request

To speed up:
- Keep server running (don't restart)
- Responses will be faster after first call
- Consider caching in React Native app

### Network IP Still Not Working
1. Check your actual IP:
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" under your active network adapter

2. Update `mlService.ts` with correct IP:
   ```typescript
   android: 'http://YOUR_ACTUAL_IP:8001/api'
   ```

3. Make sure phone and PC are on same WiFi network

4. Test from phone browser:
   - Open Chrome on Android
   - Go to: `http://YOUR_IP:8001/docs`
   - Should see API documentation

## 📱 Testing from React Native App

### 1. Check Network Connection
```typescript
// In your React Native app
const testConnection = async () => {
  try {
    const response = await fetch('http://10.54.50.182:8001/api/addiction-insights/test_user');
    const data = await response.json();
    console.log('Connection successful:', data);
  } catch (error) {
    console.error('Connection failed:', error);
  }
};
```

### 2. View Logs
```bash
# Android logs
adb logcat | grep -i "ml\|addiction\|fetch"
```

## ✨ What's Working Now

1. ✅ Server running on port 8001
2. ✅ API endpoints responding correctly
3. ✅ React Native app updated to use port 8001
4. ✅ Fallback data when MongoDB is slow
5. ✅ Error handling for network issues

## 🎯 Next Steps

1. **Add firewall rule** (see Fix 2 above)
2. **Rebuild app**: `npx expo run:android`
3. **Test on device**: Open app and check addiction insights
4. **Monitor logs**: `adb logcat` to see requests

## 💡 Pro Tips

- Keep the ML server running in a separate terminal
- First API call is always slower (3-5s)
- Subsequent calls are faster (<1s)
- Use React Native's loading states for better UX
- Consider adding request caching in the app
