import requests
import os
from dotenv import load_dotenv

load_dotenv()

def add_task(userId, title="", description=""):
    data = {
        "userId": userId,
        "name": title,
        "description": description,
    }

    url_put = f"{os.getenv('REQUEST_URL')}/tasks"
    requests.put(url_put, json=data)
