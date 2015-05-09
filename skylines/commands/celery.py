from flask.ext.script import Manager
from skylines import create_celery_app
from skylines.worker.celery import celery

manager = Manager(help="Perform operations related to the Celery task queue")


@manager.command
def runworker():
    """ Runs the Celery background worker process """
    create_celery_app()
    celery.worker_main(['skylines.worker', '--loglevel=INFO'])
