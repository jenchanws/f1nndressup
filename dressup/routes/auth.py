from flask import Blueprint, current_app, redirect, session, url_for

from dressup.auth import get_user_info, oauth

api = Blueprint("auth", __name__)


@api.route("/login")
def login():
  return oauth.twitch.authorize_redirect(
    url_for("auth.authorize", _external=True),
  )


@api.route("/authorize")
def authorize():
  token = oauth.twitch.authorize_access_token()

  resp = oauth.twitch.get(
    "https://id.twitch.tv/oauth2/validate",
    token=token,
  )
  resp.raise_for_status()
  token_info = resp.json()
  session["user_id"] = token_info["user_id"]

  user_id = int(token_info["user_id"])
  username = token_info["login"]

  session["type"] = "viewer"
  if (
    username in current_app.config["MODERATOR_ALLOWLIST"]
    and current_app.config["MODERATOR_ALLOWLIST"][username] == user_id
  ):
    session["type"] = "moderator"
  if current_app.config["STREAMER_ID"] == user_id:
    session["type"] = "streamer"

  user_info = get_user_info(user_id)
  session["username"] = user_info["display_name"]

  return redirect("/")


@api.route("/logout")
def logout():
  session.clear()
  return redirect("/")
