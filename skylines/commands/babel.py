from os import system, path

from flask.ext.script import Manager

from skylines import __title__, __version__, __email__

BABEL_FOLDER = path.join('skylines', 'frontend', 'translations')
POT_PATH = path.join(BABEL_FOLDER, 'messages.pot')

manager = Manager(help='i18n support via Flask-Babel')


def run(command):
    system(command % dict(BABEL_FOLDER=BABEL_FOLDER, POT_PATH=POT_PATH))


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

    run('pybabel update -i %(POT_PATH)s -d %(BABEL_FOLDER)s')


@manager.command
def compile():
    """ Compiles .po translations into binary .mo files """
    run('pybabel compile -d %(BABEL_FOLDER)s')
