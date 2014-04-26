var PlayButton = OpenLayers.Class(OpenLayers.Control, {
  draw: function() {
    OpenLayers.Control.prototype.draw.apply(this);
    $(this.div).on('click touchend', $.proxy(this.onClick, this));
    this.setMode('play');
    return this.div;
  },

  setMode: function(mode) {
    this.div.innerHTML = '<img src="../../images/' + mode + '.png"/>';
  },

  onClick: function(evt) {
    $(this).trigger('click');
    OpenLayers.Event.stop(evt);
  },

  CLASS_NAME: 'PlayButton'
});

