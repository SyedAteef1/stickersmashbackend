# Quick Start - ML Backend

## Install Dependencies

```bash
cd mlmodel
pip install -r requirements.txt
```

## Start the Server

```bash
python start_server.py
```

Or if that doesn't work:

```bash
python main.py
```

Or directly with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Verify Connection

1. Check server started: Should see "Server starting on http://localhost:8000"
2. Test API: Open http://localhost:8000/docs in browser
3. In your app: It should connect automatically

## Troubleshooting

### "Module not found"

```bash
pip install -r requirements.txt
```

### "Port already in use"

```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

### "Database connection error"

The backend uses `database_simple.py` (no MongoDB needed). If you see this error, check the import in `main.py`.

## That's It!

Once server is running, your app will automatically connect to it! 🎉

