from flask import redirect, request, session, url_for

from skylines import app


@app.route('/set_lang/<language>')
def set_lang(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))
