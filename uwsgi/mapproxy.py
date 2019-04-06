import os
import sys
import argparse
from mapproxy.wsgiapp import make_wsgi_app

parser = argparse.ArgumentParser(description="Run the MapProxy WSGI app.")
parser.add_argument(
    "config_file",
    nargs="?",
    metavar="mapproxy.yaml",
    help="path to the configuration YAML file",
)
args = parser.parse_args()

sys.path.append(os.path.dirname(sys.argv[0]))

from mapproxy.wsgiapp import make_wsgi_app

application = make_wsgi_app(args.config_file)
