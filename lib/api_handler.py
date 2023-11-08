import requests

def add_task(userId, title="", description=""):
    data = {
        "userId": userId,
        "name": title,
        "description": description,
    }

    url_post = f"{os.getenv('REQUEST_URL')}/tasks"
    requests.post(url_post, json=data)