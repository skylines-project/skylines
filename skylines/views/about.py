import os.path

from flask import Blueprint, render_template, current_app
from flask.ext.babel import _

from skylines.lib.helpers import markdown

about_blueprint = Blueprint('about', 'skylines')


@about_blueprint.route('/')
def about():
    return render_template('about.jinja')


@about_blueprint.route('/imprint')
def imprint():
    content = current_app.config.get(
        'SKYLINES_IMPRINT',
        'Please set the SKYLINES_IMPRINT variable in the config file.')

    return render_template(
        'generic/page-FLASK.jinja', title=_('Imprint'), content=content)


@about_blueprint.route('/team')
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
