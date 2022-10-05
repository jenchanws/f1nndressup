from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from dressup.config import Config
from dressup.models import Base


def setup_database(app):
  engine = create_engine(app.config["DATABASE_URL"])
  Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  session = scoped_session(Session)

  app.engine, app.session = engine, session


def create_session():
  engine = create_engine(Config.DATABASE_URL)
  Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  session = scoped_session(Session)
  return session
