


/**
 * A object to handle flight phase highlights.
 * @constructor
 * @param {ol.Map} _map
 * @param {slFlightCollection} _flights slFlightCollection object
 * @param {function} _padding_callback Callback method which returns the
 * correct padding for the view.
 */
slPhaseHighlighter = function(_map, _flights, _padding_callback) {
  var phase_highlighter = {};
  var phase_start_marker_style, phase_end_marker_style;
  var map = _map;
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

    map.on('postcompose', function(e) {
      var vector_context = e.vectorContext;

      if (phase_markers.start !== null) {
        vector_context.setImageStyle(phase_start_marker_style);
        vector_context.drawPointGeometry(phase_markers.start);
        vector_context.setImageStyle(phase_end_marker_style);
        vector_context.drawPointGeometry(phase_markers.end);
      }
    });

    window.flightPhaseService.addObserver('selection', function() {
      var data = window.flightPhaseService.get('selection');
      if (data) {
        phase_markers = highlight(data.start, data.end);
      } else {
        phase_markers.start = null;
        phase_markers.end = null;
      }

      map.render();
    });
  };

  phase_highlighter.init();
  return phase_highlighter;


  function highlight(start, end) {
    // the phases table should contain only phases of our first flight only
    var flight = flights.at(0);

    var start_index = getNextSmallerIndex(flight.get('time'), start);
    var end_index = getNextSmallerIndex(flight.get('time'), end);

    var phase_markers = {
      start: null,
      end: null
    };

    if (start_index >= end_index) return phase_markers;

    var coordinates = flight.get('geometry').getCoordinates();
    var extent = ol.extent.boundingExtent(coordinates.slice(start_index, end_index + 1));

    var view = map.getView();
    var buffer = Math.max(ol.extent.getWidth(extent),
                          ol.extent.getHeight(extent));
    map.getView().fit(extent, map.getSize(), { padding: getPadding() });

    var start_point = coordinates[start_index];
    var end_point = coordinates[end_index];

    phase_markers.start = new ol.geom.Point([start_point[0], start_point[1]]);
    phase_markers.end = new ol.geom.Point([end_point[0], end_point[1]]);

    return phase_markers;
  }
};
