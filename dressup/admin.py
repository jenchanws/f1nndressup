from flask import redirect, request, session, url_for
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView as BaseModelView
from flask_admin.menu import MenuLink

from dressup.models import Category


class DashboardView(AdminIndexView):
  def is_visible(self):
    return False

  @expose("/")
  def index(self):
    return redirect("/admin/category")


class ModelView(BaseModelView):
  def is_accessible(self):
    return session and session.get("type", None) in {
      "moderator",
      "streamer",
    }

  def inaccessible_callback(self, name, **kwargs):
    return redirect(url_for("auth.login", next=request.url))


class BackView(BaseView):
  @expose("/")
  def index(self):
    return redirect("/")


def setup_admin(app):
  app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
  admin = Admin(
    app,
    name="DressUp Admin",
    template_mode="bootstrap3",
    index_view=DashboardView(),
  )

  admin.add_view(BackView(name="Home"))
  admin.add_view(ModelView(Category, app.session))
