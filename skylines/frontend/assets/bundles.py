from webassets import Bundle

from .filters import SimpleClosureJS

BOWER = '../../../ember/bower_components/'

# Font Awesome

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


# Flot

flot_js = Bundle(
    BOWER + 'Flot/jquery.flot.js',
    BOWER + 'Flot/jquery.flot.time.js',
    BOWER + 'Flot/jquery.flot.crosshair.js',
    BOWER + 'Flot/jquery.flot.resize.js',
    BOWER + 'flot-marks/src/jquery.flot.marks.js',
    filters=SimpleClosureJS(disable_ie_checks=True),
    output='js/flot-%(version)s.js')


# Ember.js

ember_app_js = Bundle(
    'assets/skylines.js',
    output='js/ember-app-%(version)s.js')

ember_vendor_js = Bundle(
    'assets/vendor.js',
    output='js/ember-vendor-%(version)s.js')

ember_app_css = Bundle(
    'assets/skylines.css',
    output='css/ember-app-%(version)s.css')

ember_vendor_css = Bundle(
    'assets/vendor.css',
    output='css/ember-vendor-%(version)s.css')

# SkyLines

all_js = Bundle(
    BOWER + 'jquery/jquery.min.js',
    BOWER + 'jQuery-ajaxTransport-XDomainRequest/jquery.xdomainrequest.min.js',
    'vendor/jquery/jquery.timeago.js',
    BOWER + 'sidebar-v2/js/jquery-sidebar.min.js',
    bootstrap_js,
    filters='rjsmin',
    output='js/skylines-%(version)s.js')

upload_js = Bundle(
    BOWER + 'moment/min/moment.min.js',
    BOWER + 'eonasdan-bootstrap-datetimepicker/src/js/bootstrap-datetimepicker.js',
    'js/jquery.flot.flight-upload.js',
    filters=SimpleClosureJS,
    output='js/upload-%(version)s.js')

openlayers_js = Bundle(
    BOWER + 'BigScreen/bigscreen.min.js',
    flot_js,
    upload_js,
    output='js/ol-%(version)s.js')
