from datetime import datetime, timedelta, timezone
from flask import (
  abort,
  Blueprint,
  current_app as app,
  redirect,
  render_template,
  request,
  session,
)
from flask_sse import sse
from sqlalchemy.dialects.postgresql import array

from dressup.auth import is_admin
from dressup.models import Category, Poll

api = Blueprint("base", __name__)


@api.route("/")
def index():
  return render_template(
    "index.html.j2",
    current_poll=Poll.active(),
    is_admin=is_admin(),
    last_poll=Poll.most_recent(),
  )


@api.route("/create", methods=["GET"])
def create():
  categories = app.session.query(Category).all()
  durations = {"30s": 30, "1m": 60, "2m": 120, "3m": 180, "5m": 300}
  return render_template(
    "create.html.j2", categories=categories, durations=durations
  )


@api.route("/create", methods=["POST"])
def start_poll():
  if not is_admin():
    return redirect("/")

  if Poll.active():
    return redirect("/")

  start_time = datetime.now(timezone.utc)
  start_user = session["username"]
  categories = array(request.form.getlist("categories", int))
  duration = int(request.form.get("duration"))
  end_time = start_time + timedelta(seconds=duration)

  poll = Poll(
    start_time=start_time,
    start_user=start_user,
    end_time=end_time,
    categories=categories,
  )

  app.session.add(poll)
  app.session.commit()

  poll.set_active()

  return redirect("/")
