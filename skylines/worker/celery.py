from __future__ import absolute_import
from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name,
                    broker=app.config['BROKER_URL'],
                    include=['skylines.worker.tasks'])
    celery.config_from_object(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
