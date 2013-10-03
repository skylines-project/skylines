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
    'https://netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js',
    output='js/bootstrap-%(version)s.js')

bootstrap_css = Bundle(
    'https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css',
    'https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap-theme.min.css',
    output='css/bootstrap-%(version)s.js')


# Flot

flot_js = Bundle(
    'https://rawgithub.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/jquery.flot.js',
    'https://rawgithub.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/jquery.flot.time.js',
    'https://rawgithub.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/jquery.flot.crosshair.js',
    'https://rawgithub.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/jquery.flot.resize.js',
    'http://flot-marks.googlecode.com/svn-history/r13/trunk/src/jquery.flot.marks.js',
    'https://rawgithub.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/excanvas.min.js',
    filters=SimpleClosureJS(disable_ie_checks=True),
    output='js/flot-%(version)s.js')


# SkyLines

main_css = Bundle(
    'css/bootstrap-visibilites.css',
    'css/bootstrap-theme-skylines.css',
    'css/bootstrap-badges.css',
    'css/panel.css',
    'css/tables.css',
    'css/login-dropdown.css',
    'css/about.css',
    'css/search.css',
    'css/events.css',
    'css/tracking-table.css',
    'css/fix-table.css',
    'vendor/flags/flags.css',
    'vendor/bootstrap-datepicker/datepicker.css',
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
    'css/ol-ZoomControl.css',
    'css/map.css',
    'css/map-infobox.css',
    filters='cssmin, cssrewrite',
    output='css/ol-%(version)s.css')

datatables_css = Bundle(
    'vendor/jquery-datatables/dataTables.bootstrap.css',
    filters='cssmin, cssrewrite',
    output='css/datatables-%(version)s.css')

all_js = Bundle(
    'http://code.jquery.com/jquery-1.9.1.min.js',
    'vendor/jquery/jquery.browser.js',
    'vendor/jquery/jquery.cookie.js',
    'vendor/jquery/jquery.timeago.js',
    'js/general.js',
    bootstrap_js,
    'js/topbar.js',
    filters='rjsmin',
    output='js/skylines-%(version)s.js')

datatables_js = Bundle(
    'vendor/jquery-datatables/jquery.dataTables.js',
    'vendor/jquery-datatables/jquery.dataTables.ext.js',
    'vendor/bootstrap-datepicker/datepicker.js',
    filters=SimpleClosureJS,
    output='js/tables-%(version)s.js')

openlayers_js = Bundle(
    'vendor/openlayers/OpenLayers.js',
    'js/ol-GraphicLayerSwitcher.js',
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
