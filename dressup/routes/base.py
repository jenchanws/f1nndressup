from flask import Blueprint, render_template

api = Blueprint("base", __name__)


@api.route("/")
def index():
  return render_template("index.html.j2")
