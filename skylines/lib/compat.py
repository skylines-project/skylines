# flake8: noqa F821

import sys


def _xrange(*args, **kwargs):
    if sys.version_info[0] == 2:
        return xrange(*args, **kwargs)
    else:
        return range(*args, **kwargs)
