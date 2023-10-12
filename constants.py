import os

BASE_URL = "https://render.something" if os.getenv("ENVIRONMENT") != "dev" else "http://127.0.0.1:8000"
