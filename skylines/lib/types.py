import sys


def is_int(number):
    if sys.version_info[0] == 2:
        return isinstance(number, (int, long))
    else:
        return isinstance(number, int)
