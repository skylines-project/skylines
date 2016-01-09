var slTurnpointSelect = function(_map, _layer, _task) {
  var turnpoint_select = {};

  var map = _map;
  var layer = _layer;
  var task = _task;
  var pointer_interaction = null;

  var hovered = null;

  var hover_style = new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: '#f98000',
      width: 2
    }),
    fill: new ol.style.Fill({
      color: [0xf9, 0x80, 0x00, 0.4]
    })
  });

  turnpoint_select.init = function() {
    pointer_interaction = new ol.interaction.Pointer({
      handleEvent: handleEvent
    });

    map.addInteraction(pointer_interaction);

    $(map.getTargetElement()).on('mouseout', function(e) {
      if (hovered) {
        hovered.get('turnpoint').getSector().highlight(false);
      }
    });

    task.on('change:turnpoint:highlight', function(task, turnpoint, state) {
      turnpoint_select.highlight(task, turnpoint, state);
    });
  };

  turnpoint_select.disable = function() {
    pointer_interaction.setActive(false);
    if (hovered) {
      hovered.get('turnpoint').getSector().highlight(false);
    }
  };

  turnpoint_select.enable = function() {
    pointer_interaction.setActive(true);
  };

  turnpoint_select.highlight = function(task, turnpoint, state) {
    if (!state) {
      // remove highlight
      if (hovered) {
        hovered.setStyle(null);
        hovered = null;
      } else {
        // should never happen?!?
      }
    } else {
      // add highlight
      var _hovered = layer.getSource().getFeatures().filter(function(e) {
        return e.get('task_id') == task.cid &&
               e.get('turnpoint_id') == turnpoint.cid &&
               e.get('type') == 'turnpoint';
      })[0];

      if (!_hovered) {
        // should never happen
        return;
      }

      if (hovered) {
        // should never happen?!
        return;
      }

      hovered = _hovered;
      hovered.setStyle(hover_style);
    }
  };

  function layerFilter(candidate) {
    if (candidate === layer) return true;
    else return false;
  };

  function clickCallback(feature, layer) {
    if (feature.get('type') != 'turnpoint')
      return;

    return feature;
  };

  function hoverCallback(feature, layer) {
    if (feature.get('type') != 'turnpoint')
      return;

    return feature;
  };

  function handleClickEvent(event) {
    var clicked = map.forEachFeatureAtPixel(
        event.pixel,
        clickCallback,
        this,
        layerFilter,
        this
        );

    if (clicked)
      turnpoint_select.trigger('select', clicked);

    return true;
  };

  function handleMoveEvent(event) {
    var _hovered = map.forEachFeatureAtPixel(
        event.pixel,
        hoverCallback,
        this,
        layerFilter,
        this
        );

    if (!_hovered && hovered) {
      // Nothing hovered over. Just remove highlight.

      hovered.get('turnpoint').getSector().highlight(false);
    } else if (_hovered) {
      // Something below pointer.
      if (hovered && hovered !== _hovered) {
        // reset style of previous hovered feature
        hovered.get('turnpoint').getSector().highlight(false);
      } else if (hovered && hovered === _hovered) {
        // Nothing to do here
        return true;
      }

      // highlight turnpoint sector below pointer
      _hovered.get('turnpoint').getSector().highlight(true);
    }

    return true;
  };

  function handleEvent(event) {
    if (event.type == 'click') {
      return handleClickEvent(event);
    } else if (event.type == 'pointermove') {
      return handleMoveEvent(event);
    }
    return true;
  };

  _.extend(turnpoint_select, Backbone.Events);
  turnpoint_select.init();
  return turnpoint_select;
};
