from flask import Flask

from dressup.auth import oauth
from dressup.config import Config
from dressup.routes import setup_routes


def create_app():
  app = Flask(__name__)
  app.config.from_object(Config())

  setup_routes(app)
  oauth.init_app(app)

  return app


app = create_app()
