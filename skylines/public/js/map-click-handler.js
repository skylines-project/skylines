(function() {
  slMapClickHandler = function(infobox) {
    // Private attributes

    var map_click_handler = this;

    /**
     * The OpenLayers.Geometry object of the circle.
     * @type {Object}
     */
    var circle = null;

    /**
     * Stores the state if the infobox.
     * @type {Bool}
     */
    var visible = false;

    // Public attributes and functions

    /**
     * @expose
     * Click handler which shows a info box at the click location.
     */
    map_click_handler.trigger = function(e) {
      // do nothing if this is visible, let the event handler close the box.
      if (visible) return;

      // create bounding box in map coordinates around mouse cursor
      var pixel = new OpenLayers.Pixel(e.layerX, e.layerY);
      var clickTolerance = 15;
      var llPx = pixel.add(-clickTolerance / 2, clickTolerance / 2);
      var urPx = pixel.add(clickTolerance / 2, -clickTolerance / 2);
      var ll = map.getLonLatFromPixel(llPx);
      var ur = map.getLonLatFromPixel(urPx);
      var loc = map.getLonLatFromPixel(pixel);

      var loc_wgs84 = loc.clone()
          .transform(map.getProjectionObject(), WGS84_PROJ);
      var lon = loc_wgs84.lon,
          lat = loc_wgs84.lat;

      infobox.empty();

      // search for a aircraft position within the bounding box
      var nearest = searchForPlane(
          new OpenLayers.Bounds(ll.lon, ll.lat, ur.lon, ur.lat),
          loc,
          clickTolerance);

      if (nearest === null) return;

      var index = nearest.from;
      var flight = flights[nearest.fid];
      var dx = nearest.along;

      lon = flight.lonlat[index].lon +
          (flight.lonlat[index + 1].lon - flight.lonlat[index].lon) * dx;
      lat = flight.lonlat[index].lat +
          (flight.lonlat[index + 1].lat - flight.lonlat[index].lat) * dx;
      var time = flight.t[index] +
          (flight.t[index + 1] - flight.t[index]) * dx;

      // flight info
      var flight_info = flightInfo(flight);
      infobox.append(flight_info);

      // near flights link
      var get_near_flights = nearFlights(lon, lat, time, flight);
      infobox.append(get_near_flights);

      // general events

      map.events.register('move', this, function(e) {
        if (e.object.getExtent().containsLonLat(infobox.latlon)) {
          var pixel = e.object.getPixelFromLonLat(infobox.latlon);
          infobox.css('left', (pixel.x + 15) + 'px');
          infobox.css('top', (pixel.y - infobox.height() / 2) + 'px');
        } else {
          infobox.hide();
          hideCircle(0);
          visible = false;
        }
      });

      // hide box when clicked outside
      // use OL click event which doesn't get fired on panning
      map.events.register('click', this, function(e) {
        var outside = true;

        infobox.children().each(function() {
          if ($(this).find(e.target).length !== 0) outside = false;
        });

        if (outside) {
          infobox.hide();
          hideCircle(0);
          visible = false;
        }
      });

      infobox.latlon = new OpenLayers.LonLat(lon, lat)
          .transform(WGS84_PROJ, map.getProjectionObject());

      pixel = e.object.getPixelFromLonLat(infobox.latlon);
      infobox.css('left', (pixel.x + 15) + 'px');
      infobox.css('top', (pixel.y - infobox.height() / 2) + 'px');

      infobox.show();
      showCircle(lon, lat);

      visible = true;

      return false; // stop bubbeling
    };

    // Private functions

    function flightInfo(flight) {
      return $(
          '<span class="info-item badge" style="background:' +
              flight.color +
          '">' +
          (flight.additional && flight.additional['registration'] || '') +
          '</span>'
      );
    };

    function nearFlights(lon, lat, time, flight) {
      var get_near_flights = $(
          '<div class="info-item">' +
          '<a class="near" href="#">Load nearby flights</a>' +
          '</div>'
          );

      get_near_flights.on('click touchend', function(e) {
        infobox.hide();
        getNearFlights(lon, lat, time, flight);
        visible = false;
      });

      return get_near_flights;
    };

    /**
     * Show a circle at the clicked position
     *
     * @param {Number} lon Longitude.
     * @param {Number} lat Latitude.
     */
    function showCircle(lon, lat) {
      // first, calculate how many map units are 1000 meters. This is
      // approximate, but close enough for our purpose. In google maps
      // (and openstreetmap) spherical projection (aka EPSG:900913 or
      // EPSG:3857), one meter at the equator is exactly one unit.
      // Cut off at 85 deg.
      var distance_deg = 1000 / Math.cos(Math.PI / 180 *
          Math.min(Math.abs(lat, 85)));

      var point = new OpenLayers.Geometry.Point(lon, lat)
                  .transform(WGS84_PROJ, map.getProjectionObject());

      circle = new OpenLayers.Feature.Vector(
          new OpenLayers.Geometry.Polygon.createRegularPolygon(point,
              distance_deg, 40, 0));

      // draw this circle and fade the inner fill within 500ms
      circle.renderIntent = 'nearestCircle';

      map.getLayersByName('Flight')[0].addFeatures(circle);

      // escape points in the id, see
      // http://docs.jquery.com/Frequently_Asked_Questions#How_do_I_select_an_
      // element_by_an_ID_that_has_characters_used_in_CSS_notation.3F
      var circle_id = '#' + circle.geometry.id.replace(/(:|\.)/g, '\\$1');
      $(circle_id).animate({fillOpacity: 0}, 500);
    };

    /**
     * Hides the search circle
     *
     * @param {Integer} duration Fade duration.
     */
    function hideCircle(duration) {
      if (circle === null) return;

      var circle_id = '#' + circle.geometry.id.replace(/(:|\.)/g, '\\$1');
      // fade circle out and remove it from layer
      $(circle_id).animate({opacity: 0}, duration, function() {
        // check if circle still exists, because it might got deleted before
        // the animation was done.
        if (circle !== null) {
          map.getLayersByName('Flight')[0].destroyFeatures(circle);
          circle = null;
        }
      });
    };

    /**
     * Request near flights via ajax
     *
     * @param {Number} lon Longitude.
     * @param {Number} lat Latitude.
     * @param {Number} time Time.
     * @param {Object} flight Flight.
     */
    function getNearFlights(lon, lat, time, flight) {
      $.ajax('/flights/' + flight.sfid + '/near?lon=' + lon +
          '&lat=' + lat + '&time=' + time, {
            success: function(data) {
              for (var i = 0; i < data.flights.length; ++i) {
                // skip retrieved flight if already on map
                var next = false;
                for (var fid = 0; fid < flights.length; ++fid)
                  if (flights[fid].sfid == data.flights[i].sfid) next = true;
                  if (next) continue;

                  var flight_id = addFlight(data.flights[i].sfid,
                      data.flights[i].encoded.points,
                      data.flights[i].encoded.levels,
                      data.flights[i].num_levels,
                      data.flights[i].barogram_t,
                      data.flights[i].barogram_h,
                      data.flights[i].enl,
                      data.flights[i].zoom_levels,
                      data.flights[i].contests,
                      data.flights[i].additional);
              }
            },
            complete: function() {
              hideCircle(1000);
            }
          });
    }
  };
})();
