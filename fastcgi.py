#!/usr/bin/python
#
# Wrapper script for launching Skylines as a FastCGI in lighttpd.
#

import sys
import thread
import logging
from paste.deploy import loadapp
from flup.server.fcgi import WSGIServer

# stderr doesn't work with FastCGI; the following is a hack to get a
# log file with diagnostics anyway
sys.stderr = sys.stdout = file('/var/log/skylines/console', 'a')

prev_sys_path = list(sys.path)

new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

sys.path.append('/opt/skylines/src')

thread.stack_size(524288)

config_file = '/etc/skylines/production.ini'
wsgi_app = loadapp('config:' + config_file)
logging.config.fileConfig(config_file)

if __name__ == '__main__':
    WSGIServer(wsgi_app, minSpare=1, maxSpare=5, maxThreads=50).run()
