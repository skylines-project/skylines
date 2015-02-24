var PlayButton = function(opt_options) {
  var options = opt_options || {};
  var control = this;
  var playing = false;

  var element = document.createElement('div');
  element.className = 'PlayButton ol-unselectable';

  var draw = function() {
    $(element).on('click touchend', $.proxy(onClick, control));
    control.setMode('play');
  };

  var onClick = function(evt) {
    if (playing)
      stop();
    else
      play();

    evt.preventDefault();
  };

  var stop = function() {
    $(control).triggerHandler('stop');
    control.setMode('play');
    playing = false;
  };

  var play = function() {
    if ($(control).triggerHandler('play')) {
      control.setMode('stop');
      playing = true;
      tick();
    }
  };

  var tick = function() {
    if (!playing) return;

    if (!$(control).triggerHandler('tick')) stop();

    // schedule next call
    setTimeout(tick, 50);
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
