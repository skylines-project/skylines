#!/usr/bin/env python
#
# Extract and import PO files from a launchpad archive file
#

import os
import argparse
import tarfile
import re
import shutil

LANG_CODE_RE = re.compile(r'skylines-([a-z]{2}(?:_[A-Z_]{2})*)\.po')
I18N_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', '..', 'skylines', 'i18n')

# Parse command line arguments

parser = argparse.ArgumentParser(
    description='Extract and import PO files from a launchpad archive file.')

parser.add_argument('archive_file', metavar='launchpad-export.tar.gz',
                    help='path to the archive')

args = parser.parse_args()

# Open tar file

tar = tarfile.open(args.archive_file)


# Find PO files

def is_pofile(filename):
    return filename.endswith('.po')

po_files = filter(is_pofile, tar.getnames())


# Extract language codes from the filenames

def extract_language_code(filename):
    basename = os.path.basename(filename)
    match = LANG_CODE_RE.match(basename)
    if not match:
        raise Exception('{} is missing language code identifier.'.format(basename))

    lang_code = match.group(1)

    return (filename, lang_code)

po_files = map(extract_language_code, po_files)


# Extract PO files into i18n folder

def extract_file(fileinfo):
    filename, lang_code = fileinfo
    basename = os.path.basename(filename)

    # Ignore english translations

    if lang_code.startswith('en'):
        print 'Ignoring "{}"'.format(basename)
        return

    # Build language specific extraction path and create it if missing

    path = os.path.join(I18N_FOLDER, lang_code, 'LC_MESSAGES')
    if not os.path.exists(path):
        os.makedirs(path)

    path = os.path.join(path, 'skylines.po')

    # Extract the new PO file

    print 'Extracting "{}"'.format(basename)
    fsrc = tar.extractfile(filename)
    with open(path, 'w') as fdst:
        shutil.copyfileobj(fsrc, fdst)


map(extract_file, po_files)
