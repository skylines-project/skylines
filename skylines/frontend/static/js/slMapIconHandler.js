


/**
 * A handler to display plane icons on the map.
 * @constructor
 * @param {Object} _map ol3 map object.
 * @param {Object} _flights slFlightCollection.
 */
slMapIconHandler = function(_map, _flights) {
  var map_icon_handler = {};

  var map = _map;
  var flights = _flights;
  var hover_enabled = true;

  map_icon_handler.init = function() {
    var style = new ol.style.Icon({
      anchor: [0.5, 0.5],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      size: [40, 24],
      src: '/images/glider_symbol.png',
      rotation: 0,
      rotateWithView: true
    });

    style.load();

    map.on('pointermove', function(e) {
      if (!hover_enabled || e.dragging)
        return;

      var coordinate = map.getEventCoordinate(e.originalEvent);
      displaySnap(coordinate);
    });

    map.on('postcompose', function(e) {
      var vector_context = e.vectorContext;

      flights.each(function(flight) {
        var plane = flight.getPlane();
        if (plane.point !== null) {
          style.setRotation(plane['heading']);
          vector_context.setImageStyle(style);
          vector_context.drawPointGeometry(plane.point);
        }
      });
    });
  };

  map_icon_handler.setMode = function(mode) {
    hover_enabled = mode;
  };

  map_icon_handler.showPlane = function(flight, fix_data) {
    var plane = flight.getPlane();

    // set plane location
    if (plane.point === null) {
      plane.point = new ol.geom.Point([fix_data['lon'], fix_data['lat']]);
    } else {
      plane.point.setCoordinates([fix_data['lon'], fix_data['lat']]);
    }

    // set plane heading
    // <heading> in radians
    plane['heading'] = fix_data['heading'];

    // add plane marker if more than one flight on the map
    if (flights.length() > 1) {
      if (plane.marker === null) {
        var badge = $('<span class="badge plane_marker" ' +
                'style="display: inline-block; text-align: center; ' +
                'background: ' + flight.getColor() + ';">' +
            (flight.getCompetitionID() || '') +
            '</span>');

        plane.marker = new ol.Overlay({
          element: badge
        });
        map.addOverlay(plane.marker);
        plane.marker.setOffset([badge.width(), -40]);
      }

      plane.marker.setPosition(plane.point.getCoordinates());
    }
  };

  map_icon_handler.hidePlane = function(flight) {
    var plane = flight.getPlane();

    plane.point = null;
    if (plane.marker !== null) {
      map.removeOverlay(plane.marker);
      plane.marker = null;
    }
  };

  map_icon_handler.hideAllPlanes = function() {
    flights.each(map_icon_handler.hidePlane);
  };


  map_icon_handler.init();
  return map_icon_handler;


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
        $(map_icon_handler).triggerHandler('set_time', null);
      } else {
        var time = closest_point[3];
        $(map_icon_handler).triggerHandler('set_time', time);
      }
    }

    map.render();
  }
};
