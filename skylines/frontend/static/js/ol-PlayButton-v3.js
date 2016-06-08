/**
 * Play button control
 *
 * @constructor
 * @export
 * @param {Object=} opt_options Optional options object.
 */
var PlayButton = function(opt_options) {
  var options = opt_options || {};
  var control = this;

  control.playing = false;

  var element = document.createElement('div');
  element.className = 'PlayButton ol-unselectable';

  var draw = function() {
    $(element).on('click touchend', $.proxy(onClick, control));
    control.setMode('play');
  };

  var onClick = function(evt) {
    if (control.playing)
      stop();
    else
      play();

    evt.preventDefault();
  };

  var stop = function() {
    $(control).triggerHandler('stop');
  };

  var play = function() {
    $(control).triggerHandler('play');
  };

  ol.control.Control.call(this, {
    element: element,
    target: options.target
  });

  draw();
};

ol.inherits(PlayButton, ol.control.Control);


/**
 * Sets the playing mode.
 * @param {string} mode - Play or Stop
 */
PlayButton.prototype.setMode = function(mode) {
  this.playing = (mode === 'stop');
  this.element.innerHTML = '<img src="../../images/' + mode + '.png"/>';
};


/**
 * Gets the playing mode.
 * @return {Boolean}
 */
PlayButton.prototype.getMode = function() {
  return this.playing;
};
