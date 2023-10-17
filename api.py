from fastapi import FastAPI, Request, Response
from fastapi.logger import logger
from starlette.middleware.sessions import SessionMiddleware
from os import environ
import json
import google_auth_oauthlib.flow
from constants import BASE_URL, GOOGLE_SCOPES
from database import add_user
import logging

# Ensure that all requests include an 'example.com' or
# '*.example.com' host header, and strictly enforce https-only access.
# middleware = [
#     # Middleware(
#     #     TrustedHostMiddleware,
#     #     allowed_hosts=['example.com', '*.example.com'],
#     # ),
#     # Middleware(HTTPSRedirectMiddleware),
#     Middleware(SessionMiddleware(secret_key=environ.get('GOOGLE_CLIENT_SECRET')))
# ]

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=environ.get("GOOGLE_CLIENT_SECRET"))


@app.on_event("startup")
async def startup_event():
    global logger
    logger = logging.getLogger("uvicorn.access")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/google_oauth_callback")
async def google_oauth_callback(request: Request, response: Response):
    state, username, telegram_user_id = None, None, None
    if "state" in request.query_params:
        state_dict_dumps = request.query_params.get("state")
        if not state_dict_dumps:
            raise Exception("state not in session")
        state_dict = json.loads(state_dict_dumps)
        telegram_user_id = state_dict["telegram_user_id"]
        username = state_dict["username"]
    else:
        raise Exception("state not in session")
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config={
            "web": {
                "client_id": environ.get("GOOGLE_CLIENT_ID"),
                "project_id": "nova-401105",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": environ.get("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": ["http://127.0.0.1:8000/google_oauth_callback"],
                "javascript_origins": ["http://localhost:8000"],
            }
        },
        scopes=GOOGLE_SCOPES,
        state=state,
    )
    flow.redirect_uri = BASE_URL + "/google_oauth_callback"
    code = request.query_params.get("code")

    flow.fetch_token(code=code)

    logger.info("flow.credentials: " + str(flow.credentials))

    # Store the credentials in the session.
    credentials = flow.credentials
    request.session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        # 'token_uri': credentials.token_uri,
        "scopes": credentials.scopes,
    }

    add_user(
        telegram_user_id=int(telegram_user_id) if telegram_user_id else 0,
        username=username if username else "bad_entry",
        name=username if username else "bad_entry",
        email="",
        google_refresh_token=flow.credentials.refresh_token,
    )

    # Create a Response object with the 307 redirect status code
    response = Response(
        status_code=307, headers={"Location": "https://www.t.me/brio_tracker_bot"}
    )

    # Send the Response object
    return response
