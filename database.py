import os
from typing import List, TypedDict
from supabase.client import create_client
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

if not API_URL or not API_KEY:
    raise Exception("API_URL or API_KEY not found in .env file")

supabase = create_client(API_URL, API_KEY)


class User(TypedDict):
    telegram_user_id: int
    username: str
    name: str
    email: str
    google_refresh_token: str


def add_user(telegram_user_id, username, name, google_refresh_token, email=""):
    data: User = {
        "telegram_user_id": telegram_user_id,
        "username": username,
        "name": name,
        "email": email,
        "google_refresh_token": google_refresh_token,
    }
    supabase.table("Users").insert(dict(data)).execute()


def fetch_user(telegram_user_id) -> List[User]:
    return (
        supabase.table("Users")
        .select("*")
        .eq("telegram_user_id", telegram_user_id)
        .execute()
        .data
    )


def update_user(telegram_user_id, data):
    supabase.table("Users").update(data).eq(
        "telegram_user_id", telegram_user_id
    ).execute()


def delete_user(telegram_user_id):
    supabase.table("Users").delete().eq("telegram_user_id", telegram_user_id).execute()


def add_task(telegram_user_id, name, description=""):
    data = {
        "telegram_user_id": telegram_user_id,
        "name": name,
        "description": description,
    }
    supabase.table("Tasks").insert(data).execute()


def fetch_tasks(telegram_user_id):
    return (
        supabase.table("Tasks")
        .select("*")
        .eq("telegram_user_id", telegram_user_id)
        .eq("added", False)
        .execute()
        .data
    )


def fetch_tasks_formatted(telegram_user_id):
    tasks_json = fetch_tasks(telegram_user_id)
    tasks = ""
    for task in tasks_json:
        tasks += str(task["id"]) + ": " + task["name"] + "\n"
    return tasks


def fetch_tasks_and_id_formatted(telegram_user_id):
    tasks_json = fetch_tasks(telegram_user_id)
    tasks = ""
    for index, task in enumerate(tasks_json):
        tasks += str(index + 1) + ": " + task["name"] + "\n"
    return tasks


def mark_task_as_added(task_id):
    supabase.table("Tasks").update({"added": True}).eq("id", task_id).execute()


def delete_task(task_id):
    supabase.table("Tasks").delete().eq("id", task_id).execute()
