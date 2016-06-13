/**
 * A handler to display plane icons on the map.
 * @constructor
 * @param {Object} _map ol3 map object.
 * @param {Array} _flights
 */
slMapIconHandler = function(_map, _flights) {
  var map_icon_handler = {};

  var map = _map;
  var flights = _flights;

  map_icon_handler.showPlane = function(flight, fix_data) {
    var marker = flight.get('marker');

    // add plane marker if more than one flight on the map
    if (flights.length > 1) {
      if (!marker) {
        var badge = $('<span class="badge plane_marker" ' +
                'style="display: inline-block; text-align: center; ' +
                'background: ' + flight.get('color') + ';">' +
            flight.getWithDefault('competition_id', '') +
            '</span>');

        marker = new ol.Overlay({
          element: badge.get(0)
        });

        map.addOverlay(marker);
        flight.set('marker', marker);

        marker.setOffset([badge.width(), -40]);
      }

      marker.setPosition(fix_data.get('coordinate'));
    }
  };

  map_icon_handler.hidePlane = function(flight) {
    var marker = flight.get('marker');
    if (marker) {
      map.removeOverlay(marker);
      flight.set('marker', null);
    }
  };

  map_icon_handler.hideAllPlanes = function() {
    flights.forEach(map_icon_handler.hidePlane);
  };

  return map_icon_handler;
};
