from webassets import Environment as BaseEnvironment
from webassets.loaders import YAMLLoader
from paste.deploy.converters import asbool


class Environment(BaseEnvironment):
    """
    The Environment class can be used to manage CSS and JS assets.

    It handles the concatenation and minification of these files, performs
    client-side cache busting if the files changed and is also able to
    watch the source files for changes.

    See the webassets package for more information.
    """

    def __init__(self, config):
        # Activate debug mode to disabled concatenation and minification
        assets_debug = asbool(config.get('webassets.debug', False))

        # Activate auto build mode to build new files once the sources change
        auto_build = asbool(config.get('webassets.auto_build', False))

        # Initialize webassets Environment
        super(Environment, self).__init__(config['webassets.base_dir'],
                                          config['webassets.base_url'],
                                          debug=assets_debug,
                                          auto_build=auto_build)

        # Add folders that will be searched for source files
        load_path = config.get('webassets.load_dir', None)
        if load_path is not None:
            load_url = config.get('webassets.load_url', None)
            self.append_path(load_path, load_url)

        # Configure default closure compiler options
        self.config['CLOSURE_COMPRESSOR_OPTIMIZATION'] = 'SIMPLE_OPTIMIZATIONS'
        self.config['CLOSURE_EXTRA_ARGS'] = ['--jscomp_off', 'internetExplorerChecks']

    def load_bundles(self, bundle_file):
        """
        Load predefined bundles from a YAML file.

        See bundles.yaml for an example.
        """

        # Load bundles from YAML file
        loader = YAMLLoader(bundle_file)
        bundles = loader.load_bundles()

        # Register the bundles with the environment
        self.register(bundles)
