from flask import current_app as app
from sqlalchemy import Column, DateTime, desc, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import TIMESTAMP

from dressup.models.base import Base
from dressup.models.redis import redis


class Poll(Base):
  __tablename__ = "polls"

  id = Column(Integer, primary_key=True)

  start_time = Column(TIMESTAMP(timezone=True), nullable=False)
  start_user = Column(String(32), nullable=False)

  end_time = Column(TIMESTAMP(timezone=True), nullable=False)
  end_user = Column(String(32))

  categories = Column(ARRAY(Integer))

  @staticmethod
  def active():
    id = redis.get("dressup:active_poll")
    if id:
      return app.session.query(Poll).filter_by(id=int(id)).first()
    return None

  def set_active(self):
    redis.set("dressup:active_poll", self.id)

    duration = int((self.end_time - self.start_time).total_seconds())
    redis.expire("dressup:active_poll", duration)

  @staticmethod
  def most_recent():
    return app.session.query(Poll).order_by(desc(Poll.start_time)).first()
