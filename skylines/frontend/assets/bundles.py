from webassets import Bundle

from .filters import SimpleClosureJS


# Font Awesome

fontawesome_css = Bundle(
    'http://rawgit.com/FortAwesome/Font-Awesome/v3.2.1/css/font-awesome.css',
    output='css/fontawesome-%(version)s.css')

fontawesome_webfont_eot = Bundle(
    'http://github.com/FortAwesome/Font-Awesome/blob/v3.2.1/font/fontawesome-webfont.eot?raw=true',
    output='font/fontawesome-webfont.eot')

fontawesome_webfont_woff = Bundle(
    'http://github.com/FortAwesome/Font-Awesome/blob/v3.2.1/font/fontawesome-webfont.woff?raw=true',
    output='font/fontawesome-webfont.woff')

fontawesome_webfont_ttf = Bundle(
    'http://github.com/FortAwesome/Font-Awesome/blob/v3.2.1/font/fontawesome-webfont.ttf?raw=true',
    output='font/fontawesome-webfont.ttf')

fontawesome_webfont_svg = Bundle(
    'http://rawgit.com/FortAwesome/Font-Awesome/v3.2.1/font/fontawesome-webfont.svg',
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
    'http://rawgit.com/flot/flot/v0.8.3/jquery.flot.js',
    'http://rawgit.com/flot/flot/v0.8.3/jquery.flot.time.js',
    'http://rawgit.com/flot/flot/v0.8.3/jquery.flot.crosshair.js',
    'http://rawgit.com/flot/flot/v0.8.3/jquery.flot.resize.js',
    'http://rawgit.com/TobiasLohner/flot-marks/f09ded70f5a229a38ba0b9cfa92dbb448ca4daaf/src/jquery.flot.marks.js',
    filters=SimpleClosureJS(disable_ie_checks=True),
    output='js/flot-%(version)s.js')


# Ember.js

ember_app_js = Bundle(
    'ember/assets/skylines.js',
    output='js/ember-app-%(version)s.js')

ember_vendor_js = Bundle(
    'ember/assets/vendor.js',
    output='js/ember-vendor-%(version)s.js')

ember_app_css = Bundle(
    'ember/assets/skylines.css',
    output='css/ember-app-%(version)s.css')

ember_vendor_css = Bundle(
    'ember/assets/vendor.css',
    output='css/ember-vendor-%(version)s.css')

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
    'css/slFixTable.css',
    'css/wingman.css',
    'css/ol3-sidebar.css',
    'vendor/flags/flags.css',
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
    'vendor/openlayers/ol.css',
    'css/ol-GraphicLayerSwitcher-v3.css',
    'css/ol-PlayButton.css',
    'css/ol-FullscreenButton.css',
    'css/ol-CesiumSwitcher.css',
    'css/map.css',
    'css/map-infobox.css',
    filters='cssmin, cssrewrite',
    output='css/ol-%(version)s.css')

all_js = Bundle(
    'http://code.jquery.com/jquery-1.10.2.min.js',
    'http://cdnjs.cloudflare.com/ajax/libs/jquery-ajaxtransport-xdomainrequest/1.0.3/jquery.xdomainrequest.min.js',
    'vendor/jquery/jquery.timeago.js',
    'http://rawgit.com/Turbo87/sidebar-v2/v0.2.1/js/jquery-sidebar.min.js',
    bootstrap_js,
    filters='rjsmin',
    output='js/skylines-%(version)s.js')

openlayers_js = Bundle(
    'vendor/openlayers/ol3cesium.js',
    'http://rawgit.com/bdougherty/BigScreen/v2.0.4/bigscreen.min.js',
    flot_js,
    output='js/ol-%(version)s.js')

upload_js = Bundle(
    'http://momentjs.com/downloads/moment.min.js',
    'http://rawgit.com/TobiasLohner/bootstrap-datetimepicker/c36342415a1be8fa013548402bf01718ca93d454/src/js/bootstrap-datetimepicker.js',
    'js/jquery.flot.flight-upload.js',
    filters=SimpleClosureJS,
    output='js/upload-%(version)s.js')
