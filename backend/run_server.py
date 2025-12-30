import uvicorn
import os
import sys

if __name__ == "__main__":
    # When frozen, the executable is the entry point, but uvicorn needs to find the app.
    # We might need to adjust sys.path or how we pass the app string.
    # However, passing the app object directly avoids import string issues in frozen mode.
    
    # Add current directory to path
    if getattr(sys, 'frozen', False):
         base_dir = os.path.dirname(sys.executable)
         sys.path.insert(0, base_dir)
    else:
         base_dir = os.path.dirname(os.path.abspath(__file__))
         sys.path.insert(0, base_dir)

    try:
        from app.main import app
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"Failed to start server: {e}")
        import time
        time.sleep(10)
