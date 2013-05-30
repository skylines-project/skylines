import os

PRO_CONF_PATH = '/etc/skylines/production.py'
DEV_CONF_PATH = os.path.join('config', 'default.py')


def to_envvar(path=None):
    """
    Loads the application configuration from a file.
    Returns the configuration or None if no configuration could be found.
    """

    if path:
        if not os.path.exists(path):
            return
    elif os.path.exists(PRO_CONF_PATH):
        path = PRO_CONF_PATH
    elif os.path.exists(DEV_CONF_PATH):
        path = DEV_CONF_PATH
    else:
        return

    os.environ['SKYLINES_CONFIG'] = path
    return True
