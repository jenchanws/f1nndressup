from authlib.common.urls import add_params_to_uri
from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
from flask import session
from urllib.parse import quote

from dressup.config import Config

oauth = OAuth()

oauth.register(
  "twitch",
  client_id=Config.TWITCH_CLIENT_ID,
  client_secret=Config.TWITCH_CLIENT_SECRET,
  token_endpoint_auth_method="client_secret_post",
  authorize_url="https://id.twitch.tv/oauth2/authorize",
  authorize_params={"scope": " ".join(Config.TWITCH_AUTH_SCOPES)},
  access_token_url="https://id.twitch.tv/oauth2/token",
  api_base_url="https://api.twitch.tv/helix/",
)


def twitch():
  return OAuth2Session(
    Config.TWITCH_CLIENT_ID,
    Config.TWITCH_CLIENT_SECRET,
    token_endpoint_auth_method="client_secret_post",
  )


def get_user_info(user_id):
  with twitch() as tw:
    tok = tw.fetch_token(
      "https://id.twitch.tv/oauth2/token",
      grant_type="client_credentials",
    )
    resp = tw.get(
      "https://api.twitch.tv/helix/users",
      params=dict(id=user_id),
      headers={
        "Authorization": f"Bearer {tok['access_token']}",
        "Client-Id": Config.TWITCH_CLIENT_ID,
      },
    )
    resp.raise_for_status()
    user_info = resp.json()["data"][0]
    return user_info


def user_id():
  return session.get("user_id", None)


def user_is_following():
  with twitch() as tw:
    tok = tw.fetch_token(
      "https://id.twitch.tv/oauth2/token",
      grant_type="client_credentials",
    )
    resp = tw.get(
      "https://api.twitch.tv/helix/users/follows",
      params=dict(from_id=user_id(), to_id=Config.STREAMER_ID),
      headers={
        "Authorization": f"Bearer {tok['access_token']}",
        "Client-Id": Config.TWITCH_CLIENT_ID,
      },
    )
    resp.raise_for_status()
    follows = resp.json()["data"]
    return bool(follows)


def is_admin():
  return session.get("type", None) in {"moderator", "streamer"}
