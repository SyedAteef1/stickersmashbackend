import uvicorn
from main import app
import signal
import sys

def signal_handler(sig, frame):
    print('Server stopped by user')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    while True:
        try:
            print("Starting server on port 8001...")
            uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
        except KeyboardInterrupt:
            print("Server stopped by user")
            break
        except Exception as e:
            print(f"Server error: {e}")
            print("Restarting server in 5 seconds...")
            import time
            time.sleep(5)