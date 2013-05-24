from flask import redirect, request, session, url_for
from babel import Locale

from skylines import app


@app.babel_instance.localeselector
def select_locale():
    available = map(str, g.available_locales)
    preferred = []

    session_language = session.get('language', None)
    if session_language:
        preferred.append(session_language)

    preferred.extend([l[0] for l in request.accept_languages])

    best_match = Locale.negotiate(preferred, available)
    if best_match:
        return str(best_match)


@app.route('/set_lang/<language>')
def set_lang(language):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))
