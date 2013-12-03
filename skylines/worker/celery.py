from __future__ import absolute_import
from celery import Celery


def init_app(self, app):
    self.name = app.import_name
    self.config_from_object(app.config)

    TaskBase = self.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    self.Task = ContextTask


celery = Celery(include=['skylines.worker.tasks'])
Celery.init_app = init_app
