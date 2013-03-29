from webassets import Bundle


# Font Awesome

fontawesome_css = Bundle(
    'https://raw.github.com/FortAwesome/Font-Awesome/v3.0.2/css/font-awesome.css',
    output='css/fontawesome-%(version)s.css')

fontawesome_webfont_eot = Bundle(
    'https://github.com/FortAwesome/Font-Awesome/blob/v3.0.2/font/fontawesome-webfont.eot?raw=true',
    output='font/fontawesome-webfont.eot')

fontawesome_webfont_woff = Bundle(
    'https://github.com/FortAwesome/Font-Awesome/blob/v3.0.2/font/fontawesome-webfont.woff?raw=true',
    output='font/fontawesome-webfont.woff')

fontawesome_webfont_ttf = Bundle(
    'https://github.com/FortAwesome/Font-Awesome/blob/v3.0.2/font/fontawesome-webfont.ttf?raw=true',
    output='font/fontawesome-webfont.ttf')

fontawesome_webfont_svg = Bundle(
    'https://raw.github.com/FortAwesome/Font-Awesome/v3.0.2/font/fontawesome-webfont.svg',
    output='font/fontawesome-webfont.svg')


# Twitter Bootstrap

bootstrap_js = Bundle(
    'https://raw.github.com/twitter/bootstrap/v2.2.0/js/bootstrap-alert.js',
    'https://raw.github.com/twitter/bootstrap/v2.2.0/js/bootstrap-collapse.js',
    'https://raw.github.com/twitter/bootstrap/v2.2.0/js/bootstrap-modal.js',
    'https://raw.github.com/twitter/bootstrap/v2.2.0/js/bootstrap-tooltip.js',
    'https://raw.github.com/twitter/bootstrap/v2.2.0/js/bootstrap-popover.js',
    'https://raw.github.com/twitter/bootstrap/v2.2.0/js/bootstrap-dropdown.js',
    filters='closure_js',
    output='js/bootstrap-%(version)s.js')


# Flot

flot_js = Bundle(
    'https://raw.github.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/jquery.flot.js',
    'https://raw.github.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/jquery.flot.time.js',
    'https://raw.github.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/jquery.flot.crosshair.js',
    'https://raw.github.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/jquery.flot.resize.js',
    'http://flot-marks.googlecode.com/svn-history/r13/trunk/src/jquery.flot.marks.js',
    'https://raw.github.com/flot/flot/ccb37e4965967d7252cc99e3b2eea8fcec3c909a/excanvas.min.js',
    filters='closure_js',
    output='js/flot-%(version)s.js')


# SkyLines

main_css = Bundle(
    'css/bootstrap.min.css',
    'css/style.css',
    'css/fix-table.css',
    'css/datepicker.css',
    'images/flags.css',
    filters='cssrewrite',
    output='css/main-%(version)s.css')

all_css = Bundle(
    main_css,
    fontawesome_css,
    filters='cssmin',
    output='css/skylines-%(version)s.css')

openlayers_css = Bundle(
    'css/OpenLayers.css',
    'css/GraphicLayerSwitcher.css',
    'css/map.css',
    filters='cssmin, cssrewrite',
    output='css/ol-%(version)s.css')

datatables_css = Bundle(
    'css/dataTables.bootstrap.css',
    filters='cssmin, cssrewrite',
    output='css/datatables-%(version)s.css')

all_js = Bundle(
    'http://code.jquery.com/jquery-1.9.1.min.js',
    'js/jQuery/jquery.browser.js',
    'js/jQuery/jquery.cookie.js',
    'js/jQuery/jquery.timeago.js',
    'js/general.js',
    bootstrap_js,
    'js/topbar.js',
    filters='rjsmin',
    output='js/skylines-%(version)s.js')

datatables_js = Bundle(
    'js/jQuery/jquery.dataTables.js',
    'js/jQuery/jquery.dataTables.ext.js',
    'js/jQuery/bootstrap-datepicker.js',
    filters='closure_js',
    output='js/tables-%(version)s.js')

openlayers_js = Bundle(
    'js/OpenLayers/OpenLayers.js',
    'js/OpenLayers/GraphicLayerSwitcher.js',
    'js/map.js',
    filters='rjsmin',
    output='js/ol-%(version)s.js')

flight_js = Bundle(
    Bundle(
        'js/units.js',
        'js/baro.js',
        'js/fix-table.js',
        'js/phase-table.js',
        filters='closure_js'),

    'js/flight.js',
    filters='rjsmin',
    output='js/flight-%(version)s.js')

tracking_js = Bundle(
    'js/tracking.js',
    filters='rjsmin',
    output='js/tracking-%(version)s.js')
