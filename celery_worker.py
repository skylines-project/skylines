#!/usr/bin/env python
#
# The Celery worker daemon, which runs asyncronous tasks for SkyLines
#

from skylines import app

if __name__ == '__main__':
    with app.app_context():
        app.celery.worker_main()
