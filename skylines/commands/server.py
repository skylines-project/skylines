from flask.ext.script import Server as BaseServer
from skylines.app import create_combined_app


class Server(BaseServer):
    def handle(self, app, *args, **kw):
        app = create_combined_app()
        super(Server, self).handle(app, *args, **kw)
