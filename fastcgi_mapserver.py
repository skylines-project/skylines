#!/usr/bin/python
#
# Wrapper script for launching UMN mapserver as a FastCGI in lighttpd.
#

import sys, os
import thread
import argparse
import mapscript
from flup.server.fcgi import WSGIServer

parser = argparse.ArgumentParser(description='Run the SkyLines MapScript FastCGI daemon.')
parser.add_argument('map_file', nargs='?', metavar='airspace.map',
                    default='/opt/skylines/src/assets/airspace/airspace.map',
                    help='path to the airspace map file')
parser.add_argument('--socket', nargs='?', metavar='PATH',
                    help='path of the local socket')
parser.add_argument('--logfile', nargs='?', metavar='PATH',
                    help='path of the log file')
args = parser.parse_args()

# stderr doesn't work with FastCGI; the following is a hack to get a
# log file with diagnostics anyway
if args.logfile:
    sys.stderr = sys.stdout = file(args.logfile, 'a')

sys.path.append(os.path.dirname(sys.argv[0]))

thread.stack_size(524288)

def wsgi_app(environ, start_response):
    try:
        req = mapscript.OWSRequest()
        req.loadParamsFromURL(environ.get('QUERY_STRING'))

        map = mapscript.mapObj(args.map_file)

        mapscript.msIO_installStdoutToBuffer()
        map.OWSDispatch(req)

        content_type = mapscript.msIO_stripStdoutBufferContentType()
        content = mapscript.msIO_getStdoutBufferBytes()

        if content_type == 'vnd.ogc.se_xml':
            content_type = 'text/xml'

        start_response('200 Ok', [('Content-type', content_type)])
        return [content]
#        start_response('200 OK', [('Content-type', 'text/plain')])
#        return ['This is working already...']

    except:
        start_response('500 Ooops', [('Content-type', 'text/plain')])
        return ['An error occured\n' + mapscript.msIO_getStdoutBufferString()]

if __name__ == '__main__':
    WSGIServer(wsgi_app, bindAddress=args.socket, umask=0,
               minSpare=1, maxSpare=5, maxThreads=10).run()

