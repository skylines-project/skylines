from flask import render_template
from flask.ext.babel import _

from skylines import app


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
