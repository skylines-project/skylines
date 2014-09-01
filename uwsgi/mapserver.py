import sys, os
import argparse
import mapscript

parser = argparse.ArgumentParser(description='Run the SkyLines MapScript FastCGI daemon.')
parser.add_argument('map_file', nargs='?', metavar='airspace.map',
                    default='mapserver/airspace/airspace.map',
                    help='path to the airspace map file')
args = parser.parse_args()


def application(environ, start_response):
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

    except:
        start_response('500 Ooops', [('Content-type', 'text/plain')])
        return ['An error occured\n' + mapscript.msIO_getStdoutBufferString()]
