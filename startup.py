import subprocess
import threading
import time
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

def run_flask():
    subprocess.run(["python", "app.py"], cwd=APP_DIR)

def run_cloudflared():
    subprocess.run(["cloudflared", "tunnel", "--url", "http://127.0.0.1:5000"], cwd=APP_DIR)

if __name__ == "__main__":
    os.makedirs(os.path.join(APP_DIR, "static", "uploads"), exist_ok=True)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    time.sleep(2)
    run_cloudflared()