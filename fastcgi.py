#!/usr/bin/python
#
# Wrapper script for launching Skylines as a FastCGI in lighttpd.
#

import sys

prev_sys_path = list(sys.path)

new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

import os, sys
sys.path.append('/opt/skylines/src')

import thread
thread.stack_size(524288)

from paste.deploy import loadapp
wsgi_app = loadapp('config:/etc/skylines/production.ini')

if __name__ == '__main__':
    from flup.server.fcgi import WSGIServer
    WSGIServer(wsgi_app, minSpare=1, maxSpare=5, maxThreads=50).run()
