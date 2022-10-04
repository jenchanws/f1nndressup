from dressup.routes.auth import api as auth
from dressup.routes.base import api as base


def setup_routes(app):
  app.register_blueprint(auth)
  app.register_blueprint(base)
