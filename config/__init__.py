import os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

PRO_CONF_PATH = '/etc/skylines/production.py'
DEFAULT_CONF_PATH = os.path.join(BASE_PATH, 'default.py')
TESTING_CONF_PATH = os.path.join(BASE_PATH, 'testing.py')


def to_envvar(path=None):
    """
    Loads the application configuration from a file.
    Returns the configuration or None if no configuration could be found.
    """

    if path:
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return
    elif os.path.exists(PRO_CONF_PATH):
        path = PRO_CONF_PATH
    else:
        return True

    os.environ['SKYLINES_CONFIG'] = path
    return True
