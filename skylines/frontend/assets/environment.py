from flask.ext.assets import Environment as BaseEnvironment
from webassets.loaders import PythonLoader


class Environment(BaseEnvironment):
    """
    The Environment class can be used to manage CSS and JS assets.

    It handles the concatenation and minification of these files, performs
    client-side cache busting if the files changed and is also able to
    watch the source files for changes.

    See the webassets package for more information.
    """

    def __init__(self, app):
        # Initialize webassets Environment
        super(Environment, self).__init__(app)

        # Add folders that will be searched for source files
        load_path = app.config.get('ASSETS_LOAD_DIR', None)
        if load_path is not None:
            load_url = app.config.get('ASSETS_LOAD_URL', None)
            self.append_path(load_path, load_url)

    def load_bundles(self, module):
        """
        Load predefined bundles from a YAML file.

        See bundles.yaml for an example.
        """

        # Load bundles from YAML file
        loader = PythonLoader(module)
        bundles = loader.load_bundles()

        # Register the bundles with the environment
        self.register(bundles)
