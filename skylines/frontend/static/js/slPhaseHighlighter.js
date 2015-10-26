


/**
 * A object to handle flight phase highlights.
 * @constructor
 * @param {slMap} _map slMap object.
 * @param {Object} _baro slBarogram object.
 * @param {slFlightCollection} _flights slFlightCollection object
 * @param {function} _padding_callback Callback method which returns the
 * correct padding for the view.
 */
slPhaseHighlighter = function(_map, _baro, _flights, _padding_callback) {
  var phase_tables = [];

  var phase_highlighter = {};
  var phase_start_marker_style, phase_end_marker_style;
  var map = _map;
  var baro = _baro;
  var flights = _flights;
  var getPadding = _padding_callback ?
      _padding_callback : function() { return [0, 0, 0, 0]; };

  var phase_markers = {
    start: null,
    end: null
  };

  phase_highlighter.init = function() {
    phase_start_marker_style = new ol.style.Icon({
      anchor: [0.5, 1],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      src: '/vendor/openlayers/img/marker-green.png'
    });

    phase_end_marker_style = new ol.style.Icon({
      anchor: [0.5, 1],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      src: '/vendor/openlayers/img/marker.png'
    });

    phase_start_marker_style.load();
    phase_end_marker_style.load();

    map.getMap().on('postcompose', function(e) {
      var vector_context = e.vectorContext;

      if (phase_markers.start !== null) {
        vector_context.setImageStyle(phase_start_marker_style);
        vector_context.drawPointGeometry(phase_markers.start);
        vector_context.setImageStyle(phase_end_marker_style);
        vector_context.drawPointGeometry(phase_markers.end);
      }
    });
  };


  phase_highlighter.addTable = function(placeholder) {
    if (placeholder.length === 0 || placeholder.data('phase_table')) return;

    var phase_table = slPhaseTable(placeholder);

    placeholder.data('phase_table', phase_table);
    phase_tables.push(phase_table);

    $(phase_table)
        .on('selection_changed', function(event, data) {
          if (data) {
            phase_markers = highlight(data.start, data.end);
            baro.setTimeHighlight(data.start, data.end);

            for (var i = 0; i < phase_tables.length; i++) {
              if (phase_tables[i] != this) {
                phase_tables[i].setSelection(null, false);
              }
            }
          } else {
            phase_markers.start = null;
            phase_markers.end = null;

            baro.clearTimeHighlight();
          }

          baro.draw();
          map.getMap().render();
        });
  };

  phase_highlighter.init();
  return phase_highlighter;


  function highlight(start, end) {
    // the phases table should contain only phases of our first flight only
    var flight = flights.at(0);

    var start_index = getNextSmallerIndex(flight.getTime(), start);
    var end_index = getNextSmallerIndex(flight.getTime(), end);

    var phase_markers = {
      start: null,
      end: null
    };

    if (start_index >= end_index) return phase_markers;

    var extent = ol.extent.boundingExtent(
        flight.getGeometry().getCoordinates().slice(start_index, end_index + 1)
        );

    var view = map.getMap().getView();
    var buffer = Math.max(ol.extent.getWidth(extent),
                          ol.extent.getHeight(extent));
    map.getMap().getView().fit(extent,
                               map.getMap().getSize(),
                               { padding: getPadding() });

    var start_point = flight.getGeometry().getCoordinates()[start_index];
    var end_point = flight.getGeometry().getCoordinates()[end_index];

    phase_markers.start = new ol.geom.Point([start_point[0], start_point[1]]);
    phase_markers.end = new ol.geom.Point([end_point[0], end_point[1]]);

    return phase_markers;
  }
};
