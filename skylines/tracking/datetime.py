from __future__ import absolute_import

from datetime import time


def ms_to_time(ms):
    ms = ms % (24 * 3600 * 1000)

    hour = int((ms / (1000 * 60 * 60)) % 24)
    minute = int((ms / (1000 * 60)) % 60)
    second = int((ms / 1000) % 60)
    millisecond = int(ms % 1000)

    return time(hour, minute, second, millisecond)
