from flask import redirect, request, session, url_for, g
from flask.ext.babel import get_locale
from babel import Locale
from babel.util import distinct


def register(app):
    available_locales = {
        str(l): l for l in app.babel_instance.list_translations()
    }

    def _get_preferred_languages():
        preferred = []

        session_language = session.get('language', None)
        if session_language:
            preferred.append(str(session_language))

        preferred.extend([l[0] for l in request.accept_languages])
        return preferred

    def _get_primary_locales():
        preferred = _get_preferred_languages() or ['en']
        primary = []

        for language in preferred:
            if language in available_locales:
                primary.append(available_locales[language])
            elif language[:2] in available_locales:
                primary.append(available_locales[language[:2]])

        return map(None, distinct(primary))

    @app.before_request
    def inject_active_locale():
        g.available_locales = available_locales.values()
        g.active_locale = get_locale()

        g.primary_locales = _get_primary_locales()
        g.secondary_locales = \
            [l for l in g.available_locales if l not in g.primary_locales]

    @app.babel_instance.localeselector
    def select_locale():
        available = available_locales.keys()
        preferred = _get_preferred_languages()

        # Find best match
        best_match = Locale.negotiate(preferred, available)

        # Return best match
        if best_match:
            return str(best_match)

    @app.route('/set_lang/<language>')
    def set_lang(language):
        session['language'] = language
        return redirect(request.referrer or url_for('index'))
