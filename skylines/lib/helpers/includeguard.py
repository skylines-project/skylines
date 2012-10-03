from sets import Set
from os.path import normpath
from inspect import currentframe, getframeinfo

from tg import request

__all__ = ['not_included_yet']


def not_included_yet():
    # Create template_includes set if necessary
    if not hasattr(request, 'template_includes'):
        request.template_includes = Set()

    # Extract calling template filename
    filename = normpath(getframeinfo(currentframe(1)).filename)

    # Check whether template was already included before
    if filename in request.template_includes:
        return False

    # Remember that this template was included now
    request.template_includes.add(filename)
    return True
