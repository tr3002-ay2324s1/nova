import os

BASE_URL = "https://tele-bot-server.onrender.com:10000" if os.getenv("ENVIRONMENT") != "dev" else "http://127.0.0.1:8000"
