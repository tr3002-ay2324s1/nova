import os
import json
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
supabase = create_client(API_URL, API_KEY)

def add_user(telegram_user_id, username, name, email, google_refresh_token):
    data = {
        'telegram_user_id': telegram_user_id,
        'username': username,
        'name': name,
        'email': email,
        'google_refresh_token': google_refresh_token
    }
    supabase.table('Users').insert(data).execute()

def fetch_user(telegram_user_id):
    return supabase.table('Users').select('*').eq('telegram_user_id', telegram_user_id).execute().data

def update_user(telegram_user_id, data):
    supabase.table('Users').update(data).eq('telegram_user_id', telegram_user_id).execute()

def delete_user(telegram_user_id):
    supabase.table('Users').delete().eq('telegram_user_id', telegram_user_id).execute()
