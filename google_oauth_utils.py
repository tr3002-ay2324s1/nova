from google_auth_oauthlib.flow import Flow
import json

async def get_login_google(telegram_user_id: int, username: str):
  # Use the credentials.json file to identify the application requesting
  # authorization. The client ID (from that file) and access scopes are required.
  flow = Flow.from_client_secrets_file(
      'credentials.json',
      scopes=['https://www.googleapis.com/auth/calendar.events'])

  # Indicate where the API server will redirect the user after the user completes
  # the authorization flow. The redirect URI is required. The value must exactly
  # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
  # configured in the API Console. If this value doesn't match an authorized URI,
  # you will get a 'redirect_uri_mismatch' error.
  flow.redirect_uri = 'http://127.0.0.1:8000/google_oauth_callback'

  # Generate URL for request to Google's OAuth 2.0 server.
  # Use kwargs to set optional request parameters.
  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true',
      state=json.dumps({
        "telegram_user_id": str(telegram_user_id),
        "username": username
      })
    )

  return authorization_url, state
