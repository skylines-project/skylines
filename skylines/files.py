# -*- coding: utf-8 -*-
"""This library helps storing data files in the server file system."""

import os, shutil
import re
from tg import config

def sanitise_filename(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    name = os.path.basename(name)
    name = re.sub(r'[^-_.a-zA-Z0-9]', '_', name)
    name = unicode(name)
    name = name.lstrip('.')
    name = name.lower()
    if name == '':
        name = 'empty'
    return name

def filename_to_path(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    return os.path.join(config['skylines.files.path'], name)

def open_file(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    return file(filename_to_path(name))

def next_filename(name):
    assert isinstance(name, str) or isinstance(name, unicode)

    i = name.rfind('.')
    if i < 0:
        i = len(name)
    return name[:i] + '_' + name[i:]

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
    except OSError, e:
        pass
