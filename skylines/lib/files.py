# -*- coding: utf-8 -*-
"""This library helps storing data files in the server file system."""

import os
import shutil
import re

from flask import current_app

igc_filename_numbers_regex = re.compile(r"([\w_-]+)_(\d+)")


def sanitise_filename(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    # strip the parent directory name
    name = os.path.basename(name)

    # replace all non-ASCII or dangerous characters
    name = re.sub(r'[^-_.a-zA-Z0-9]', '_', name)

    # convert to unicode string
    name = unicode(name)

    # dots at the beginning of a file name are "special", remove them
    name = name.lstrip('.')

    # normalise to lower case
    name = name.lower()

    # empty file names are illegal, replace
    if name == '':
        name = 'empty'
    return name


def filename_to_path(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    return os.path.join(current_app.config['SKYLINES_FILES_PATH'], name)


def open_file(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    return file(filename_to_path(name))


def next_filename(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    i = name.rfind('.')

    match = igc_filename_numbers_regex.match(name[:i])

    try:
        number = int(match.group(2))
        return "%s_%i%s" % (match.group(1), number + 1, name[i:])

    except AttributeError:
        pass

    return "%s_1%s" % (name[:i], name[i:])


def add_file(name, f):
    assert isinstance(name, str) or isinstance(name, unicode)

    while True:
        path = filename_to_path(name)
        if not os.access(path, os.F_OK):
            break
        name = next_filename(name)

    dest = file(path, 'w')
    shutil.copyfileobj(f, dest)
    dest.close()

    return name


def delete_file(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    path = filename_to_path(name)
    try:
        os.unlink(path)
    except OSError:
        pass
