import os
from tg import config


def helper_path(helper):
    return os.path.join(config['skylines.analysis.path'], helper)
