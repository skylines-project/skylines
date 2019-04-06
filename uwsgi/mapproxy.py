import os
import sys
from mapproxy.wsgiapp import make_wsgi_app

sys.path.append(os.path.dirname(sys.argv[0]))

config_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "mapproxy", "mapproxy.yaml"
)
application = make_wsgi_app(config_file)
