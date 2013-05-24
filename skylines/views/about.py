from flask import render_template

from skylines import app


@app.route('/about')
def about():
    return render_template('about.jinja')
