from flask import redirect, request, session, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView as BaseModelView

from dressup.models import Category


class ModelView(BaseModelView):
  def is_accessible(self):
    return session and session.get("type", None) in {
      "moderator",
      "streamer",
    }

  def inaccessible_callback(self, name, **kwargs):
    return redirect(url_for("auth.login", next=request.url))


def setup_admin(app):
  app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
  admin = Admin(app, template_mode="bootstrap3")

  admin.add_view(ModelView(Category, app.session))
