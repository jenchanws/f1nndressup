from datetime import datetime, timezone
from flask import current_app as app, session
from flask_sse import sse
from sqlalchemy import Column, DateTime, desc, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.types import TIMESTAMP

from dressup.models.base import Base
from dressup.models.category import Category
from dressup.models.redis import redis
from dressup.database import create_session
from dressup.schedule import sched


class Poll(Base):
  __tablename__ = "polls"

  id = Column(Integer, primary_key=True)

  start_time = Column(TIMESTAMP(timezone=True), nullable=False)
  start_user = Column(String(32), nullable=False)

  end_time = Column(TIMESTAMP(timezone=True), nullable=False)
  end_user = Column(String(32))

  categories = Column(ARRAY(Integer))
  final_votes = Column(JSON(none_as_null=True))

  @staticmethod
  def active():
    id = redis.get("poll:active")
    if id:
      return app.session.query(Poll).filter_by(id=int(id)).first()
    return None

  def set_active(self):
    redis.set("poll:active", self.id)

    duration = int((self.end_time - self.start_time).total_seconds())
    redis.expire("poll:active", duration)

    sched.add_job(
      f"cleanup-{self.id}",
      Poll.cleanup,
      args=[self.id],
      next_run_time=self.end_time,
    )

    sse.publish(None, type="poll-start")

  def votes_in_category(self, category):
    counts = [
      redis.hget(f"poll:{self.id}:votes:{category.id}", opt)
      for opt in category.options
    ]
    counts = [int(c) if c else 0 for c in counts]
    total = sum(counts)

    percentages = [round(100 * c / total) if total else 0 for c in counts]

    return list(zip(category.options, counts, percentages))

  def record_vote(self, user_id, votes):
    for cat, option in votes.items():
      redis.hincrby(f"poll:{self.id}:votes:{cat}", option, 1)
    redis.sadd(f"poll:{self.id}:voted", user_id)
    sse.publish(self.info(), type="vote")

  def poll(self):
    if self.final_votes:
      return self.final_votes

    categories = (
      app.session.query(Category)
      .filter(Category.id.in_(self.categories[:]))
      .all()
    )
    return {
      c.id: (
        c.display_name,
        self.votes_in_category(c),
      )
      for c in categories
    }

  def info(self):
    if self.final_votes:
      return {"poll": self.final_votes}
    return {"poll": self.poll()}

  def has_vote_from(self, user_id):
    return bool(redis.sismember(f"poll:{self.id}:voted", user_id))

  @staticmethod
  def most_recent():
    return app.session.query(Poll).order_by(desc(Poll.start_time)).first()

  def end(self, requester):
    self.final_votes = self.poll()

    self.end_time = datetime.now(timezone.utc)
    self.end_user = requester

    app.session.add(self)
    app.session.commit()

    redis.delete("poll:active")
    redis.persist("poll:active")

    redis.delete(
      *(f"poll:{self.id}:votes:{category}" for category in self.categories[:])
    )
    redis.delete(f"poll:{self.id}:voted")

    sse.publish(None, type="poll-end")

  @staticmethod
  def cleanup(id):
    session = create_session()
    poll = session.query(Poll).filter_by(id=id).first()
    if not poll:
      return

    categories = (
      session.query(Category).filter(Category.id.in_(poll.categories[:])).all()
    )
    poll.final_votes = {
      c.id: (
        c.display_name,
        poll.votes_in_category(c),
      )
      for c in categories
    }
    session.add(poll)
    session.commit()

    redis.delete("poll:active")
    redis.persist("poll:active")

    redis.delete(
      *(f"poll:{id}:votes:{category}" for category in poll.categories[:])
    )
    redis.delete(f"poll:{id}:voted")
