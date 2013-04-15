/* Copyright (c) 2006-2013 by OpenLayers Contributors (see authors.txt for
 * full list of contributors). Published under the 2-clause BSD license.
 * See license.txt in the OpenLayers distribution or repository for the
 * full text of the license. */

var GraphicLayerSwitcher = OpenLayers.Class(OpenLayers.Control, {
  layerStates: null,
  layersDiv: null,

  /**
   * @param {Object} options
   */
  initialize: function(options) {
    OpenLayers.Control.prototype.initialize.apply(this, arguments);
    this.layerStates = [];
  },

  destroy: function() {
    OpenLayers.Event.stopObservingElement(this.div);

    //clear out layers info and unregister their events
    this.map.events.un({
      'addlayer': this.redraw,
      'changelayer': this.redraw,
      'removelayer': this.redraw,
      'changebaselayer': this.redraw,
      scope: this
    });
    OpenLayers.Control.prototype.destroy.apply(this, arguments);
  },

  /**
   * @param {<OpenLayers.Map>} map
   */
  setMap: function(map) {
    OpenLayers.Control.prototype.setMap.apply(this, arguments);

    this.map.events.on({
      'addlayer': this.redraw,
      'changelayer': this.redraw,
      'removelayer': this.redraw,
      'changebaselayer': this.redraw,
      scope: this
    });
  },

  /**
   * @return {DOMElement} A reference to the DIV DOMElement containing the
   *   switcher tabs.
   */
  draw: function() {
    OpenLayers.Control.prototype.draw.apply(this);
    this.loadContents();
    this.redraw();
    return this.div;
  },

  /**
   * Checks if the layer state has changed since the last redraw() call.
   *
   * @return {Boolean} The layer state changed since the last redraw() call.
   */
  checkRedraw: function() {
    var redraw = false;
    if (!this.layerStates.length ||
        (this.map.layers.length != this.layerStates.length)) {
      redraw = true;
    } else {
      for (var i = 0, len = this.layerStates.length; i < len; i++) {
        var layerState = this.layerStates[i];
        var layer = this.map.layers[i];
        if ((layerState.name != layer.name) ||
            (layerState.inRange != layer.inRange) ||
            (layerState.id != layer.id)) {
          redraw = true;
          break;
        }
      }
    }
    return redraw;
  },

  /**
   * Goes through and takes the current state of the Map and rebuilds the
   * control to display that state.
   *
   * @return {DOMElement} A reference to the DIV DOMElement containing
   *   the control.
   */
  redraw: function() {
    if (!this.checkRedraw()) {
      return this.div;
    }

    this.div.innerHTML = '';

    var len = this.map.layers.length;
    this.layerStates = [];
    for (var i = 0; i < this.map.layers.length; i++) {
      var layer = this.map.layers[i];
      this.layerStates[i] = {
        'name': layer.name,
        'visibility': layer.visibility,
        'inRange': layer.inRange,
        'id': layer.id
      };
    }

    var layers = this.map.layers.slice();

    var layer_switcher = $('<div class="box"></div>');
    var base_layers = $('<div class="base"></div>');
    var overlay_layers = $('<div class="overlay"></div>');

    var current = $('<img src="../../images/layers.png" class="current"/>');

    current.on('click touchend', function(e) {
      current.hide();
      layer_switcher.show();
      e.stopPropagation();
    });

    $(this.div).append(current);


    for (var i = 0; i < layers.length; i++) {
      var layer = layers[i];
      var baseLayer = layer.isBaseLayer;
      var id = this.id + '_input_' + layer.name.replace(/ /g, '_');

      if (layer.displayInLayerSwitcher) {
        // populate base layer box
        var layer_visible = baseLayer ?
            (layer == this.map.baseLayer) : layer.getVisibility();

        var layer_image = '../../images/layers/' + layer.name +
            (layer_visible ? '.png' : '.bw.png');

        var item = $(
            "<a id='" + id + "' href='#LayerSwitcher'>" +
            "<img src='" + layer_image + "' />" +
            layer.name +
            '</a><br />');

        if (layer_visible)
          item.addClass('active');

        item.on('click touchend', $.proxy(this.onInputClick,
            {'layerSwitcher': this, 'layer': layer}));

        if (baseLayer) {
          item.on('mouseover touchstart', $.proxy(function() {
            if (this.layer != this.map.baseLayer) {
              $('#' + this.id).find('img').attr('src',
                  '../../images/layers/' + this.layer.name + '.png');

              $('.GraphicLayerSwitcher .base .active').find('img').attr('src',
                  '../../images/layers/' + this.map.baseLayer.name + '.bw.png');
            }
          }, { id: id, layer: layer, map: this.map}));

          item.on('mouseout touchend', $.proxy(function() {
            if (this.layer != this.map.baseLayer) {
              $('#' + this.id).find('img').attr('src',
                  '../../images/layers/' + this.layer.name + '.bw.png');

              $('.GraphicLayerSwitcher .base .active').find('img').attr('src',
                  '../../images/layers/' + this.map.baseLayer.name + '.png');
            }
          }, { id: id, layer: layer, map: this.map }));

          base_layers.append(item);
        } else {
          overlay_layers.append(item);
        }

      }
    }

    // hide box when clicked outside
    $(document).on('mouseup touchend', function(e) {
      if (base_layers.find(e.target).length === 0 &&
          overlay_layers.find(e.target).length === 0) {
        layer_switcher.hide();
        current.show();
      }
    });

    // close selector box when inactive for 5 seconds
    var close_timeout = false;
    $(this.div).on('mousemove touchstart', function() {
      clearTimeout(close_timeout);
      close_timeout = setTimeout(function() {
        layer_switcher.hide();
        current.show();
      }, 5000);
    });

    layer_switcher.append(base_layers);
    layer_switcher.append(overlay_layers);

    $(this.div).append(layer_switcher);

    // prevent mouse events bubbling throu the overlay
    base_layers.on('mouseup', $.proxy(this.mouseUp, this));
    base_layers.on('mousedown', $.proxy(this.mouseDown, this));

    overlay_layers.on('mouseup', $.proxy(this.mouseUp, this));
    overlay_layers.on('mousedown', $.proxy(this.mouseDown, this));

    return this.div;
  },

  updateLayerItems: function() {
    for (var i = 0; i < this.map.layers.length; i++) {
      var layer = this.map.layers[i];
      var baseLayer = layer.isBaseLayer;

      var id = this.id + '_input_' + layer.name.replace(/ /g, '_');

      if (layer.displayInLayerSwitcher) {
        // populate base layer box
        var layer_visible = baseLayer ?
            (layer == this.map.baseLayer) : layer.getVisibility();

        var layer_image = '../../images/layers/' + layer.name +
            (layer_visible ? '.png' : '.bw.png');

        $('#' + id).find('img').attr('src', layer_image);

        if (layer_visible) {
          $('#' + id).addClass('active');
        } else {
          $('#' + id).removeClass('active');
        }
      }
    }
  },

  onInputClick: function(e) {
    if (this.layer.isBaseLayer) {
      this.layer.map.setBaseLayer(this.layer);
      $.cookie('base_layer', this.layer.name, { path: '/', expires: 365 });
    } else {
      this.layer.setVisibility(!this.layer.getVisibility());

      overlay_layers = [];
      for (var i = 0; i < this.layer.map.layers.length; ++i) {
        var layer = this.layer.map.layers[i];
        if (!layer.isBaseLayer &&
            layer.visibility &&
            layer.displayInLayerSwitcher)
          overlay_layers.push(layer.name);
      }

      $.cookie('overlay_layers', overlay_layers.join(';'), {
        path: '/',
        expires: 365
      });
    }

    this.layerSwitcher.updateLayerItems();
    OpenLayers.Event.stop(e);
  },

  /**
   * Cycles through the loaded data and base layer input arrays and makes
   * the necessary calls to the Map object such that that the map's
   * visual state corresponds to what the user has selected in the control.
   */
  updateMap: function() {
    // set the newly selected base layer
    for (var i = 0, len = this.baseLayers.length; i < len; i++) {
      var layerEntry = this.baseLayers[i];
      if (layerEntry.inputElem.checked) {
        this.map.setBaseLayer(layerEntry.layer, false);
      }
    }

    // set the correct visibilities for the overlays
    for (var i = 0, len = this.dataLayers.length; i < len; i++) {
      var layerEntry = this.dataLayers[i];
      layerEntry.layer.setVisibility(layerEntry.inputElem.checked);
    }
  },

  /**
   * Set up the labels and divs for the control
   */
  loadContents: function() {
    OpenLayers.Event.observe(this.div, 'click',
        this.ignoreEvent);
    OpenLayers.Event.observe(this.div, 'dblclick', this.ignoreEvent);
  },

  ignoreEvent: function(evt) {
    OpenLayers.Event.stop(evt);
  },

  mouseDown: function(evt) {
    this.isMouseDown = true;
    this.ignoreEvent(evt);
  },

  mouseUp: function(evt) {
    if (this.isMouseDown) {
      this.isMouseDown = false;
      this.ignoreEvent(evt);
    }
  },

  CLASS_NAME: 'GraphicLayerSwitcher'
});

