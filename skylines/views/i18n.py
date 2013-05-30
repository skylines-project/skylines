from flask import redirect, request, session, url_for, g
from flask.ext.babel import get_locale
from babel import Locale
from formencode.api import set_stdtranslation


def register(app):
    """"""

    available_locales = app.babel_instance.list_translations()

    @app.before_request
    def inject_active_locale():
        g.available_locales = available_locales
        g.active_locale = get_locale()

    @app.babel_instance.localeselector
    def select_locale():
        available = map(str, available_locales)
        preferred = []

        session_language = session.get('language', None)
        if session_language:
            preferred.append(session_language)

        preferred.extend([l[0] for l in request.accept_languages])

        # Find best match
        best_match = Locale.negotiate(preferred, available)

        # Configure FormEncode library
        set_formencode_language(best_match or 'en')

        # Return best match
        if best_match:
            return str(best_match)

    def set_formencode_language(language):
        set_stdtranslation(languages=[str(language)])

    @app.route('/set_lang/<language>')
    def set_lang(language):
        session['language'] = language
        return redirect(request.referrer or url_for('index'))
