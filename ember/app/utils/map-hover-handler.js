/* globals $ */

export default function slMapHoverHandler(_map, _flights) {
  var map_hover_handler = {};

  var map = _map;
  var flights = _flights;
  var hover_enabled = true;

  map_hover_handler.init = function() {
    map.on('pointermove', function(e) {
      if (!hover_enabled || e.dragging)
        return;

      var coordinate = map.getEventCoordinate(e.originalEvent);
      displaySnap(coordinate);
    });
  };

  map_hover_handler.setMode = function(mode) {
    hover_enabled = mode;
  };


  map_hover_handler.init();
  return map_hover_handler;


  function displaySnap(coordinate) {
    var flight_path_source = flights.getSource();

    var closest_feature = flight_path_source
        .getClosestFeatureToCoordinate(coordinate);

    if (closest_feature !== null) {
      var geometry = closest_feature.getGeometry();
      var closest_point = geometry.getClosestPoint(coordinate);

      var feature_pixel = map.getPixelFromCoordinate(closest_point);
      var mouse_pixel = map.getPixelFromCoordinate(coordinate);

      var squared_distance = Math.pow(mouse_pixel[0] - feature_pixel[0], 2) +
                             Math.pow(mouse_pixel[1] - feature_pixel[1], 2);

      if (squared_distance > 100) {
        $(map_hover_handler).triggerHandler('set_time', null);
      } else {
        var time = closest_point[3];
        $(map_hover_handler).triggerHandler('set_time', time);
      }
    }

    map.render();
  }
}
