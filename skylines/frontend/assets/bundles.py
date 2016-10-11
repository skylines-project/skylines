from webassets import Bundle

ember_app_js = Bundle(
    'assets/skylines.js',
    output='ember-app-%(version)s.js')

ember_vendor_js = Bundle(
    'assets/vendor.js',
    output='ember-vendor-%(version)s.js')

ember_app_css = Bundle(
    'assets/skylines.css',
    output='ember-app-%(version)s.css')

ember_vendor_css = Bundle(
    'assets/vendor.css',
    output='ember-vendor-%(version)s.css')
