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
from dressup.config import Config
from dressup.models import Category, Poll

api = Blueprint("base", __name__)


@api.route("/")
def index():
  poll = Poll.active()
  can_vote = (
    poll is not None
    and session.get("user_id", False)
    and not poll.has_vote_from(session["user_id"])
  )
  return render_template(
    "index.html.j2",
    current_poll=poll,
    can_vote=can_vote,
    is_admin=is_admin(),
    last_poll=Poll.most_recent(),
  )


@api.route("/create", methods=["GET"])
def create():
  categories = app.session.query(Category).all()
  return render_template(
    "create.html.j2", categories=categories, durations=Config.DURATIONS
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


@api.route("/end", methods=["POST"])
def end():
  if not is_admin():
    return redirect("/")

  poll = Poll.active()

  if not poll:
    return redirect("/")

  poll.end(requester=session["username"])
  return redirect("/")


@api.route("/vote", methods=["POST"])
def vote():
  if not session:
    return redirect("/")

  poll = Poll.active()

  if not poll:
    return redirect("/")

  vote = {int(key.split("-", 1)[1]): val for key, val in request.form.items()}
  poll.record_vote(session["user_id"], vote)
  return redirect("/")
