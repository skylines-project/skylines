import os

from flask import current_app


def helper_path(helper):
    return os.path.join(current_app.config['SKYLINES_ANALYSIS_PATH'], helper)
