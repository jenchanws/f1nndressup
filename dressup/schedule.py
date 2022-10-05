from flask import current_app as app
from flask_apscheduler import APScheduler as BaseAPScheduler


class APScheduler(BaseAPScheduler):
  def run_job(self, id, jobstore=None):
    with app.app_context():
      super().run_job(id=id, jobstore=jobstore)


sched = APScheduler()
