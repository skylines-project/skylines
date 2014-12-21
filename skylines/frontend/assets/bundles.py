from webassets import Bundle

from .filters import SimpleClosureJS


# Font Awesome

fontawesome_css = Bundle(
    'https://rawgithub.com/FortAwesome/Font-Awesome/v3.2.1/css/font-awesome.css',
    output='css/fontawesome-%(version)s.css')

fontawesome_webfont_eot = Bundle(
    'https://github.com/FortAwesome/Font-Awesome/blob/v3.2.1/font/fontawesome-webfont.eot?raw=true',
    output='font/fontawesome-webfont.eot')

fontawesome_webfont_woff = Bundle(
    'https://github.com/FortAwesome/Font-Awesome/blob/v3.2.1/font/fontawesome-webfont.woff?raw=true',
    output='font/fontawesome-webfont.woff')

fontawesome_webfont_ttf = Bundle(
    'https://github.com/FortAwesome/Font-Awesome/blob/v3.2.1/font/fontawesome-webfont.ttf?raw=true',
    output='font/fontawesome-webfont.ttf')

fontawesome_webfont_svg = Bundle(
    'https://rawgithub.com/FortAwesome/Font-Awesome/v3.2.1/font/fontawesome-webfont.svg',
    output='font/fontawesome-webfont.svg')


# Twitter Bootstrap

bootstrap_js = Bundle(
    'https://netdna.bootstrapcdn.com/bootstrap/3.0.2/js/bootstrap.min.js',
    output='js/bootstrap-%(version)s.js')

bootstrap_css = Bundle(
    'https://netdna.bootstrapcdn.com/bootstrap/3.0.2/css/bootstrap.min.css',
    'https://netdna.bootstrapcdn.com/bootstrap/3.0.2/css/bootstrap-theme.min.css',
    output='css/bootstrap-%(version)s.js')


# Flot

flot_js = Bundle(
    'https://rawgithub.com/flot/flot/v0.8.3/jquery.flot.js',
    'https://rawgithub.com/flot/flot/v0.8.3/jquery.flot.time.js',
    'https://rawgithub.com/flot/flot/v0.8.3/jquery.flot.crosshair.js',
    'https://rawgithub.com/flot/flot/v0.8.3/jquery.flot.resize.js',
    'http://flot-marks.googlecode.com/svn-history/r13/trunk/src/jquery.flot.marks.js',
    'https://rawgithub.com/flot/flot/v0.8.3/excanvas.min.js',
    filters=SimpleClosureJS(disable_ie_checks=True),
    output='js/flot-%(version)s.js')


# Respond.js

respond_js = Bundle(
    'https://cdnjs.cloudflare.com/ajax/libs/respond.js/1.3.0/respond.min.js',
    output='js/respond-%(version)s.js')


# SkyLines

main_css = Bundle(
    'css/bootstrap-visibilites.css',
    'css/bootstrap-theme-skylines.css',
    'css/bootstrap-badges.css',
    'css/bootstrap-vertical-tabs.css',
    'css/bootstrap-datetimepicker.css',
    'css/panel.css',
    'css/follower-panel.css',
    'css/tables.css',
    'css/login-dropdown.css',
    'css/about.css',
    'css/search.css',
    'css/events.css',
    'css/tracking-table.css',
    'css/fix-table.css',
    'css/wingman.css',
    'vendor/flags/flags.css',
    'vendor/bootstrap-datepicker/datepicker.css',
    'vendor/fonts/stylesheet.css',
    filters='cssrewrite',
    output='css/main-%(version)s.css')

all_css = Bundle(
    bootstrap_css,
    main_css,
    fontawesome_css,
    filters='cssmin',
    output='css/skylines-%(version)s.css')

openlayers_css = Bundle(
    'vendor/openlayers/OpenLayers.css',
    'css/ol-GraphicLayerSwitcher.css',
    'css/ol-PlayButton.css',
    'css/ol-ZoomControl.css',
    'css/map.css',
    'css/map-infobox.css',
    filters='cssmin, cssrewrite',
    output='css/ol-%(version)s.css')

all_js = Bundle(
    'http://code.jquery.com/jquery-1.10.2.min.js',
    'vendor/jquery/jquery.browser.js',
    'vendor/jquery/jquery.cookie.js',
    'vendor/jquery/jquery.timeago.js',
    'vendor/bootstrap-datepicker/datepicker.js',
    'js/general.js',
    bootstrap_js,
    filters='rjsmin',
    output='js/skylines-%(version)s.js')

openlayers_js = Bundle(
    'vendor/openlayers/OpenLayers.js',
    'js/ol-GraphicLayerSwitcher.js',
    'js/ol-PlayButton.js',
    'js/map.js',
    'js/map-click-handler.js',
    filters=SimpleClosureJS,
    output='js/ol-%(version)s.js')

flight_js = Bundle(
    Bundle(
        'js/units.js',
        'js/baro.js',
        'js/fix-table.js',
        'js/phase-table.js',
        'js/collection.js',
        filters=SimpleClosureJS),

    'js/flight.js',
    filters='rjsmin',
    output='js/flight-%(version)s.js')

tracking_js = Bundle(
    'js/tracking.js',
    filters='rjsmin',
    output='js/tracking-%(version)s.js')

upload_js = Bundle(
    'js/units.js',
    'js/baro.js',
    'js/upload.js',
    'http://momentjs.com/downloads/moment.min.js',
    'https://rawgithub.com/TobiasLohner/bootstrap-datetimepicker/7cf8cb30ad2322417d78742346f080a4889d449e/src/js/bootstrap-datetimepicker.js',
    'js/jquery.flot.flight-upload.js',
    filters=SimpleClosureJS,
    output='js/upload-%(version)s.js')
