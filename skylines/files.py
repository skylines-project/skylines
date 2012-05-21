# -*- coding: utf-8 -*-
"""This library helps storing data files in the server file system."""

import os, shutil
import re
from tg import config

def sanitise_filename(name):
    import unicodedata
    if not isinstance(name, unicode):
        name = unicode(name)
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
    name = re.sub(r'[^-_.a-zA-Z0-9]', '_', name)
    name = name.lstrip('.')
    if name == '':
        name = 'empty'
    return name

def filename_to_path(name):
    return os.path.join(config['skylines.files.path'], name)

def add_file(name, f):
    path = filename_to_path(name)
    dest = file(path, 'w')
    shutil.copyfileobj(f, dest)
    dest.close()
