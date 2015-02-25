/**
 * Graphic layer switcher for base layers and overlay layers.
 *
 * @constructor
 * @param {Object=} opt_options Options
 */
var GraphicLayerSwitcher = function(opt_options) {
  var options = opt_options || {};

  var control = this;

  var element = document.createElement('div');
  element.className = 'GraphicLayerSwitcher ol-unselectable';

  /**
   * Initially draws the layer switcher
   */
  var draw = function() {
    // closed layer switcher icon
    var anchor = $('<button><img src="../../images/layers.png" /></button>');

    // closed layer switcher box
    var anchor_box = $('<div id="GraphicLayerSwitcher-closed"></div>');
    anchor_box.append(anchor);

    $(element).append(anchor_box);

    // open layer switcher box
    var layer_switcher_box =
        $('<div id="GraphicLayerSwitcher-open">asdf</div>');
    layer_switcher_box.hide();

    $(element).append(layer_switcher_box);

    // open layer switcher on click on anchor
    anchor.on('click touchend', function(e) {
      update(layer_switcher_box);
      anchor_box.hide();
      layer_switcher_box.show();
      e.stopPropagation();
    });

    // close layer switcher on click outside
    $(document).on('mouseup touchend', function(e) {
      if ($(layer_switcher_box).find('.base_layers').find(e.target).length ==
          0 &&
          $(layer_switcher_box).find('.overlay_layers').find(e.target).length ==
          0) {
        layer_switcher_box.hide();
        anchor_box.show();
      }
    });
  };

  /**
   * Updates the layer switcher according to the current layer state
   *
   * @param {jQuery} layer_switcher_box jQuery element of the layer switcher
   */
  var update = function(layer_switcher_box) {
    // empty layer switcher box...
    layer_switcher_box.empty();

    // get all layers of the map
    var layers = control.getMap().getLayers().getArray();

    var base_layers = $('<div class="base_layers"></div>');
    var overlay_layers = $('<div class="overlay_layers"></div>');

    for (var i = 0; i < layers.length; i++) {
      var layer = layers[i];

      if (layer.get('display_in_layer_switcher')) {
        // populate base layer box
        var layer_visible = layer.getVisible();

        var layer_image = '../../images/layers/' + layer.get('name') +
            (layer_visible ? '.png' : '.bw.png');

        var item = $(
            "<a href='#GraphicLayerSwitcher' id='GraphicLayerSwitcher-" +
            layer.get('id') +
            "'>" +
            "<img src='" + layer_image + "' />" +
            "<i class='icon-ok' />" +
            layer.get('name') +
            '</a>');

        if (layer_visible)
          item.addClass('active');

        item.on('click', null, { layer: layer }, onInputClick);

        item.on('mouseover touchstart', null, { item: item, layer: layer },
            function(e) {
              $(e.data.item).find('img').attr('src',
                  '../../images/layers/' + e.data.layer.get('name') + '.png');
            });

        item.on('mouseout touchend', null, { item: item, layer: layer },
            function(e) {
              if (!e.data.layer.getVisible()) {
                $(e.data.item).find('img').attr('src',
                    '../../images/layers/' + e.data.layer.get('name') +
                    '.bw.png');
              }
            });

        if (layer.get('base_layer')) {
          base_layers.append(item);
        } else {
          overlay_layers.append(item);
        }
      }
    }

    layer_switcher_box.append(base_layers);
    layer_switcher_box.append(overlay_layers);
  };

  /**
   * Event handler for the click event
   * @param {Event} e Event
   */
  var onInputClick = function(e) {
    var layer = e.data.layer;
    if (layer.get('base_layer')) {
      control.getMap().getLayers().forEach(function(other_layer) {
        if (other_layer.get('base_layer')) {
          var item = $(element)
              .find('#GraphicLayerSwitcher-' + other_layer.get('id'));
          var img;

          if (other_layer.get('name') == layer.get('name')) {
            other_layer.setVisible(true);
            img = '../../images/layers/' + other_layer.get('name') + '.png';
            item.addClass('active');
          } else {
            other_layer.setVisible(false);
            img = '../../images/layers/' + other_layer.get('name') + '.bw.png';
            item.removeClass('active');
          }
          item.find('img').attr('src', img);
        }
      });

      $.cookie('base_layer',
               layer.get('name'),
               { path: '/', expires: 365 });

    } else {
      layer.setVisible(!layer.getVisible());

      var item = $(element).find('#GraphicLayerSwitcher-' + layer.get('id'));
      item.toggleClass('active');

      overlay_layers = [];
      for (var i = 0; i < control.getMap().getLayers().getArray().length; ++i) {
        var other_layer = control.getMap().getLayers().item(i);
        if (!other_layer.get('base_layer') &&
            other_layer.getVisible() &&
            other_layer.get('display_in_layer_switcher'))
          overlay_layers.push(other_layer.get('name'));
      }

      $.cookie('overlay_layers', overlay_layers.join(';'), {
        path: '/',
        expires: 365
      });
    }

    // prevent #GrapicLayerSwitcher to be appended to the URI
    e.preventDefault();
  };

  ol.control.Control.call(this, {
    element: element,
    target: options.target
  });

  draw();
};

ol.inherits(GraphicLayerSwitcher, ol.control.Control);
