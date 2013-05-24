import os.path

from flask import render_template
from flask.ext.babel import _

from skylines import app
from skylines.lib.helpers import markdown


@app.route('/about')
def about():
    return render_template('about.jinja')


@app.route('/about/imprint')
def imprint():
    content = app.config.get(
        'SKYLINES_IMPRINT',
        'Please set the SKYLINES_IMPRINT variable in the config file.')

    return render_template(
        'generic/page-FLASK.jinja', title=_('Imprint'), content=content)


@app.route('/about/team')
def skylines_team():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', '..', 'AUTHORS.md')
    with open(path) as f:
        content = f.read().decode('utf-8')

    content = content.replace('Developers', _('Developers'))
    content = content.replace('Translators', _('Translators'))

    content = markdown.convert(content)

    return render_template('generic/page-FLASK.jinja',
                           title=_('The SkyLines Team'),
                           content=content)
