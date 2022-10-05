from flask import Flask
from flask_sse import sse

from dressup.admin import setup_admin
from dressup.auth import oauth
from dressup.database import setup_database
from dressup.config import Config
from dressup.models.redis import redis
from dressup.routes import setup_routes
from dressup.schedule import sched


def create_app():
  app = Flask(__name__)
  app.config.from_object(Config())

  setup_routes(app)
  setup_database(app)
  setup_admin(app)
  oauth.init_app(app)
  redis.init_app(app)

  sched.init_app(app)
  sched.start()

  app.register_blueprint(sse, url_prefix="/stream")

  return app


app = create_app()
