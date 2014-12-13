from webassets import Bundle

from .filters import SimpleClosureJS

BOWER = '../../../bower_components/'

# Font Awesome

fontawesome_css = Bundle(
    BOWER + 'font-awesome/css/font-awesome.css',
    output='css/fontawesome-%(version)s.css')

fontawesome_webfont_eot = Bundle(
    BOWER + 'font-awesome/font/fontawesome-webfont.eot',
    output='font/fontawesome-webfont.eot')

fontawesome_webfont_woff = Bundle(
    BOWER + 'font-awesome/font/fontawesome-webfont.woff',
    output='font/fontawesome-webfont.woff')

fontawesome_webfont_ttf = Bundle(
    BOWER + 'font-awesome/font/fontawesome-webfont.ttf',
    output='font/fontawesome-webfont.ttf')

fontawesome_webfont_svg = Bundle(
    BOWER + 'font-awesome/font/fontawesome-webfont.svg',
    output='font/fontawesome-webfont.svg')


# Twitter Bootstrap

bootstrap_js = Bundle(
    BOWER + 'bootstrap/dist/js/bootstrap.min.js',
    output='js/bootstrap-%(version)s.js')

bootstrap_css = Bundle(
    BOWER + 'bootstrap/dist/css/bootstrap.min.css',
    BOWER + 'bootstrap/dist/css/bootstrap-theme.min.css',
    output='css/bootstrap-%(version)s.js')


# Flot

flot_js = Bundle(
    BOWER + 'flot/jquery.flot.js',
    BOWER + 'flot/jquery.flot.time.js',
    BOWER + 'flot/jquery.flot.crosshair.js',
    BOWER + 'flot/jquery.flot.resize.js',
    BOWER + 'flot.marks/index.js',
    BOWER + 'flot/excanvas.min.js',
    filters=SimpleClosureJS(disable_ie_checks=True),
    output='js/flot-%(version)s.js')


# Respond.js

respond_js = Bundle(
    BOWER + 'respond/respond.min.js',
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
    'vendor/fonts/stylesheet.css',
    filters='cssrewrite',
    output='css/main-%(version)s.css')

all_css = Bundle(
    bootstrap_css,
    main_css,
    fontawesome_css,
    BOWER + 'bootstrap-datepicker/css/datepicker.css',
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
    BOWER + 'jquery/jquery.js',
    BOWER + 'jquery.browser/dist/jquery.browser.js',
    BOWER + 'jquery.cookie/jquery.cookie.js',
    BOWER + 'jquery-timeago/jquery.timeago.js',
    BOWER + 'bootstrap-datepicker/js/bootstrap-datepicker.js',
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
    BOWER + 'moment/moment.js',
    BOWER + 'bootstrap-datetimepicker/index.js',
    'js/jquery.flot.flight-upload.js',
    filters=SimpleClosureJS,
    output='js/upload-%(version)s.js')
