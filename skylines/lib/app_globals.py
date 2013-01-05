# -*- coding: utf-8 -*-

"""The application's Globals object"""

from tg import config
from skylines.assets import Environment

__all__ = ['Globals']


class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """

    def __init__(self):
        # Initialize webassets environment
        self.assets = Environment(config)

        # Load predefined bundles from YAML file
        self.assets.load_bundles(config['webassets.bundles_file'])
