var GraphicLayerSwitcher = OpenLayers.Class(OpenLayers.Control, {
  layerStates: null,
  layersDiv: null,
  ascending: true,

  initialize: function(options) {
    OpenLayers.Control.prototype.initialize.apply(this, arguments);
     this.layerStates = [];
  },

  destroy: function() {
    OpenLayers.Event.stopObservingElement(this.div);

    //clear out layers info and unregister their events 
    this.map.events.un({
      "addlayer": this.redraw,
      "changelayer": this.redraw,
      "removelayer": this.redraw,
      "changebaselayer": this.redraw,
      scope: this
    });
    OpenLayers.Control.prototype.destroy.apply(this, arguments);
  },

  setMap: function(map) {
    OpenLayers.Control.prototype.setMap.apply(this, arguments);

    this.map.events.on({
      "addlayer": this.redraw,
      "changelayer": this.redraw,
      "removelayer": this.redraw,
      "changebaselayer": this.redraw,
      scope: this
    });
  },

  draw: function() {
    OpenLayers.Control.prototype.draw.apply(this);
    this.loadContents();
    this.redraw();
    return this.div;
  },

  checkRedraw: function() {
    var redraw = false;
    if ( !this.layerStates.length ||
         (this.map.layers.length != this.layerStates.length) ) {
      redraw = true;
    } else {
      for (var i=0, len=this.layerStates.length; i<len; i++) {
        var layerState = this.layerStates[i];
        var layer = this.map.layers[i];
        if ( (layerState.name != layer.name) ||
             (layerState.inRange != layer.inRange) ||
             (layerState.id != layer.id) ||
             (layerState.visibility != layer.visibility) ) {
          redraw = true;
          break;
        }
      }
    }
    return redraw;
  },

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

    var current = $(
      "<a href='#'>" +
        "<img src='../../images/layers.png' />" +
      "</a>");
    current.addClass('GraphicLayerSwitcher current');

    current.on('click touchstart', function(e) {
      $(this).hide();
      $('.GraphicLayerSwitcher.box').show();
    });

    $(this.div).append(current);

    var layer_switcher = $("<div class='GraphicLayerSwitcher box'></div>");

    var base_layers = $("<div class='base'></div>");
    if (!this.ascending) { layers.reverse(); }
    for (var i = 0; i < layers.length; i++) {
      var layer = layers[i];
      var baseLayer = layer.isBaseLayer;

      // populate base layer box
      if (layer.displayInLayerSwitcher && baseLayer) {
        var on = (baseLayer) ? (layer == this.map.baseLayer)
                    : layer.getVisibility();
        

        var id = this.id + '_input_' + layer.name.replace(/ /g, '_');

        var layer_image = '../../images/layers/' + layer.name +
          (on ? '.png' : '.bw.png');

        var base_item = $(
          "<a id='" + id + "' href='#'>" +
            "<img src='" + layer_image + "' />" +
            layer.name +
          "</a><br />");

        if (on) {

          base_item.addClass('active');

        }
        
        base_item.on('click touchend', $.proxy(this.onInputClick, {'layer': layer}));

        base_item.on('mouseover touchstart', $.proxy(function() {
          if (this.name != this.active) {
            $('#' + this.id).find('img').attr('src', '../../images/layers/' + this.name + '.png');

            $('.GraphicLayerSwitcher.base .active').find('img')
              .attr('src', '../../images/layers/' + this.active + '.bw.png');
          }
        }, { id: id, name: layer.name, active: this.map.baseLayer.name }));

        base_item.on('mouseout touchend', $.proxy(function() {
          if (this.name != this.active) {
            $('#' + this.id).find('img').attr('src', '../../images/layers/' + this.name + '.bw.png');

            $('.GraphicLayerSwitcher.base .active').find('img')
              .attr('src', '../../images/layers/' + this.active + '.png');
          }
        }, { id: id, name: layer.name, active: this.map.baseLayer.name }));

        $(base_layers).append(base_item);
      }
    }

    // hide box when clicked outside
    $(document).mouseup(function (e) {
      if ($('.GraphicLayerSwitcher.box').has(e.target).length === 0) {
        $('.GraphicLayerSwitcher.box').hide();
        $('.GraphicLayerSwitcher.current').show();
      }
    });

    // close selector box when inactive for 5 seconds
    var close_timeout = false;
    $(this.div).on('mousemove', function() {
      clearTimeout(close_timeout);
      close_timeout = setTimeout(function() {
        $('.GraphicLayerSwitcher.box').hide();
        $('.GraphicLayerSwitcher.current').show();
      }, 5000);
    });

    layer_switcher.append(base_layers);
    $(this.div).append(layer_switcher);
    return this.div;
  },

  onInputClick: function(e) {
    if (this.layer.isBaseLayer) {
      this.layer.map.setBaseLayer(this.layer);
    } else {
      this.layer.setVisibility(!this.layer.getVisibility());
    }

    $('.GraphicLayerSwitcher.box').hide();
    $('.GraphicLayerSwitcher.current').show();
    OpenLayers.Event.stop(e);
  },

  updateMap: function() {

    // set the newly selected base layer
    for(var i=0, len=this.baseLayers.length; i<len; i++) {
      var layerEntry = this.baseLayers[i];
      if (layerEntry.inputElem.checked) {
        this.map.setBaseLayer(layerEntry.layer, false);
      }
    }

    // set the correct visibilities for the overlays
    for(var i=0, len=this.dataLayers.length; i<len; i++) {
      var layerEntry = this.dataLayers[i];
      layerEntry.layer.setVisibility(layerEntry.inputElem.checked);
    }

  },

  loadContents: function() {
    //configure main div
    OpenLayers.Event.observe(this.div, 'mouseup',
      OpenLayers.Function.bindAsEventListener(this.mouseUp, this));
    OpenLayers.Event.observe(this.div, 'click',
      this.ignoreEvent);
    OpenLayers.Event.observe(this.div, 'mousedown',
      OpenLayers.Function.bindAsEventListener(this.mouseDown, this));
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

  CLASS_NAME: "GraphicLayerSwitcher"
});

