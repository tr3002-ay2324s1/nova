from typing import List, TypedDict
from requests import request, post
from os import getenv


class Task(TypedDict):
    userId: str
    name: str
    duration: int
    deadline: str  # MMDD


def get_user(user_id: str):
    # Make a HTTP request to BASE_URL/users/{user_id}

    user_res = request(
        method="GET",
        url=f"{getenv('REQUEST_URL')}/users/telegram/" + user_id,
        headers={
            "Content-Type": "application/json",
        },
    )

    user = user_res.json()
    return user


def add_tasks(tasks: List[Task]):
    url_post = f"{getenv('REQUEST_URL')}/tasks"
    post(url_post, json=tasks)
