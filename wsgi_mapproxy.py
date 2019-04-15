import os
from mapproxy.wsgiapp import make_wsgi_app

config_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mapproxy", "mapproxy.yaml"
)
application = make_wsgi_app(config_file)
