var PlayButton = function(opt_options) {
  var options = opt_options || {};
  var control = this;

  var element = document.createElement('div');
  element.className = 'PlayButton ol-unselectable';

  var draw = function() {
    $(element).on('click touchend', $.proxy(onClick, control));
    control.setMode('play');
  };

  var onClick = function(evt) {
    $(this).trigger('click');
    evt.preventDefault();
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
  this.element.innerHTML = '<img src="../../images/' + mode + '.png"/>';
};
