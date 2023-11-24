from typing import List, TypedDict
from requests import request, post, patch
from os import getenv

from utils.constants import BASE_URL


class Task(TypedDict):
    userId: str
    name: str
    duration: int
    deadline: str  # MMDD


class Habit(TypedDict):
    userId: str
    name: str
    frequency: int


def get_google_oauth_login_url(telegram_user_id: str, username: str):
    # Make a HTTP GET request to BASE_URL/get_google_oauth_url

    url = f"{BASE_URL}/get_google_oauth_url"
    res = request(
        method="GET",
        url=url,
        headers={
            "Content-Type": "application/json",
        },
        params={
            "telegram_user_id": telegram_user_id,
            "username": username,
        },
    )

    url: str = res.json()["url"]
    return url


def get_user(telegram_user_id: str):
    # Make a HTTP request to BASE_URL/users/telegram/{user_id}

    user_res = request(
        method="GET",
        url=f"{BASE_URL}/users/telegram/" + telegram_user_id,
        headers={
            "Content-Type": "application/json",
        },
    )

    user = user_res.json()
    return user


async def add_tasks(task: Task):
    url_post = f"{BASE_URL}/tasks"
    response = post(url_post, json=task)
    return response.json()


def mark_task_as_added(task_id: int):
    url_patch = f"{BASE_URL}/tasks/added/{task_id}"
    patch(url_patch)


async def plan_tasks(telegram_user_id: str):
    url_patch = f"{BASE_URL}/tasks/plan/telegram/{telegram_user_id}"
    response = patch(url_patch)
    return response.json()
