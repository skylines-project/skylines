#!/usr/bin/env python

import os
import sys
import glob
import re
import polib
import nose
from collections import Counter

re_python_new = re.compile(r'\{(\w*)\}')
re_python_old = re.compile(r'%(?:\((\w+)\))?(\w+)')


def get_language_code(filename):
    filename = os.path.split(filename)[0]
    filename = os.path.split(filename)[0]
    filename = os.path.split(filename)[1]
    return filename


def test_pofiles():
    for filename in glob.glob(os.path.join('skylines', 'i18n', '*', 'LC_MESSAGES', 'skylines.po')):
        test_pofiles.func_doc = ('Python string format placeholders must match '
                                 '(lang: {})'.format(get_language_code(filename)))
        yield check_pofile, filename


def check_pofile(filename):
    po = polib.pofile(filename)
    for entry in po.translated_entries():
        if not entry.obsolete and not entry.msgstr == '':
            check_placeholders(filename, entry.msgid, entry.msgstr)


def check_placeholders(filename, msgid, msgstr):
    check_python(filename, msgid, msgstr, re_python_new)
    check_python(filename, msgid, msgstr, re_python_old)


def check_python(filename, msgid, msgstr, re):
    matches_orig = re.findall(msgid)
    if len(matches_orig) == 0:
        return

    matches_trans = re.findall(msgstr)

    counter_orig = Counter()
    for match in matches_orig:
        counter_orig[match] += 1

    counter_trans = Counter()
    for match in matches_trans:
        counter_trans[match] += 1

    assert counter_trans == counter_orig, \
        (u'Python string format placeholders are not matching up!\n\n'
         'File: {}\n\n'
         'Original: {}\n'
         'Translation: {}'.format(filename, msgid, msgstr))

if __name__ == "__main__":
    sys.argv.append(__name__)
    nose.run()
