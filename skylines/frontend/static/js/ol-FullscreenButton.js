/**
 * Fullscreen control
 *
 * @constructor
 * @export
 * @param {jQuery} target Element to use for fullscreen
 * @param {Object=} opt_options Optional options object.
 */
var FullscreenButton = function(target, opt_options) {
  var options = opt_options || {};
  var control = this;

  var element = document.createElement('div');

  var draw = function() {
    // fullscreen mode available?
    if (!BigScreen.enabled)
      return;

    element.className = 'FullscreenButton ol-unselectable';
    element.innerHTML = '<i class="icon-fullscreen"></i>';

    $(element).on('click touchend', function(e) {
      BigScreen.toggle(target[0]);
    });
  };

  ol.control.Control.call(this, {
    element: element,
    target: options.target
  });

  draw();
};

ol.inherits(FullscreenButton, ol.control.Control);
