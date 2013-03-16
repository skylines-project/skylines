# -*- coding: utf-8 -*-

import hashlib


def file_md5(f):
    """Return the hex MD5 digest of a file-like object."""

    md5 = hashlib.md5()
    for chunk in iter(lambda: f.read(8192), b''):
        md5.update(chunk)
    return md5.hexdigest()
