from fastapi import FastAPI, Request, Response
from starlette.middleware.sessions import SessionMiddleware
from os import environ

import google_auth_oauthlib.flow


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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/google_oauth_callback")
async def google_oauth_callback(request: Request, response: Response):
  if "state" in request.session:
    state = request.session['state']
  else:
    state = None
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/calendar.events'],
    state=state
    )
  flow.redirect_uri = 'http://127.0.0.1:8000/google_oauth_callback'
  code = request.query_params.get("code")
  print("CODE", code)
  flow.fetch_token(code=code)

  # Store the credentials in the session.
  # ACTION ITEM for developers:
  #     Store user's access and refresh tokens in your data store if
  #     incorporating this code into your real app.
  credentials = flow.credentials
  request.session['credentials'] = {
      'token': credentials.token,
      'refresh_token': credentials.refresh_token,
      # 'token_uri': credentials.token_uri,
      'client_id': credentials.client_id,
      'client_secret': credentials.client_secret,
      'scopes': credentials.scopes
  }

  # TODO: Save refresh token and create user row in DB

  # Create a Response object with the 307 redirect status code
  response = Response(status_code=307, headers={'Location': 'https://www.t.me/brio_tracker_bot'})

  # Send the Response object
  return response
