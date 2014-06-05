import os
import re
import shutil
import tarfile

from flask.ext.script import Manager, Command, Option

from skylines import __title__, __version__, __email__

BABEL_FOLDER = os.path.join('skylines', 'frontend', 'translations')
POT_PATH = os.path.join(BABEL_FOLDER, 'messages.pot')
LANG_CODE_RE = re.compile(r'translations-([a-z]{2}(?:_[A-Z_]{2})*)\.po')


class LaunchpadImport(Command):
    """ Extract and import PO files from a launchpad archive file """

    option_list = (
        Option('archive_file', metavar='launchpad-export.tar.gz',
               help='path to the archive'),
    )

    def run(self, archive_file):
        # Open tar file
        tar = tarfile.open(archive_file)

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

            path = os.path.join(BABEL_FOLDER, lang_code, 'LC_MESSAGES')
            if not os.path.exists(path):
                os.makedirs(path)

            path = os.path.join(path, 'messages.po')

            # Extract the new PO file

            print 'Extracting "{}"'.format(basename)
            fsrc = tar.extractfile(filename)
            with open(path, 'w') as fdst:
                shutil.copyfileobj(fsrc, fdst)

        map(extract_file, po_files)


manager = Manager(help='i18n support via Flask-Babel')
manager.add_command('import-launchpad', LaunchpadImport())


def run(command):
    os.system(command % dict(BABEL_FOLDER=BABEL_FOLDER, POT_PATH=POT_PATH))


@manager.command
def extract():
    """
    Extracts localizable messages and generates a .pot translation template
    """

    run('pybabel extract'
        ' --project="' + __title__ + '"'
        ' --version="' + __version__ + '"'
        ' --copyright-holder="' + __title__ + ' team"'
        ' --msgid-bugs-address="' + __email__ + '"'
        ' -F %(BABEL_FOLDER)s/babel.cfg'
        ' -k l_'
        ' -w 79'
        ' -o %(POT_PATH)s .')


@manager.option('language', help='language code of the new translation')
def init(language):
    """ Creates a new .po translation for the specified language """
    run('pybabel init -i %(POT_PATH)s -d %(BABEL_FOLDER)s -l ' + language)


@manager.command
def update():
    """
    Merges new translations from the .pot translation template into the
    .po translations
    """

    run('pybabel update -i %(POT_PATH)s -d %(BABEL_FOLDER)s -w 79')


@manager.command
def compile():
    """ Compiles .po translations into binary .mo files """
    run('pybabel compile -d %(BABEL_FOLDER)s')
