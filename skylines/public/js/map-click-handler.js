(function() {
  slMapClickHandler = function(infobox, settings) {
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

      var pixel = e.object.events.getMousePosition(e);

      var loc = map.getLonLatFromPixel(pixel);

      var loc_wgs84 = loc.clone()
          .transform(map.getProjectionObject(), WGS84_PROJ);
      var lon = loc_wgs84.lon,
          lat = loc_wgs84.lat;

      infobox.stop(true, true); // remove any running delays or animations
      infobox.empty();

      if (settings.flight_info) {
        // create bounding box in map coordinates around mouse cursor
        var clickTolerance = 15;
        var llPx = pixel.add(-clickTolerance / 2, clickTolerance / 2);
        var urPx = pixel.add(clickTolerance / 2, -clickTolerance / 2);
        var ll = map.getLonLatFromPixel(llPx);
        var ur = map.getLonLatFromPixel(urPx);

        var bounds = new OpenLayers.Bounds(ll.lon, ll.lat, ur.lon, ur.lat);

        // search for a aircraft position within the bounding box
        var nearest = searchForPlane(bounds, loc, clickTolerance);

        if (nearest !== null) {
          var index = nearest.from;
          var flight = nearest.flight;
          var dx = nearest.along;

          var lonlat_prev = flight.lonlat[index];
          var lonlat_next = flight.lonlat[index + 1];
          lon = lonlat_prev.lon + (lonlat_next.lon - lonlat_prev.lon) * dx;
          lat = lonlat_prev.lat + (lonlat_next.lat - lonlat_prev.lat) * dx;

          var time_prev = flight.t[index];
          var time_next = flight.t[index + 1];
          var time = time_prev + (time_next - time_prev) * dx;

          // flight info
          var flight_info = flightInfo(flight);
          infobox.append(flight_info);

          // near flights link
          var get_near_flights = nearFlights(lon, lat, time, flight);
          infobox.append(get_near_flights);
        }
      }

      if (settings.location_info) {
        // location info
        var get_location_info = locationInfo(lon, lat);
        infobox.append(get_location_info);
      }

      // general events

      map.events.register('move', this, function(e) {
        if (e.object.getExtent().scale(2).containsLonLat(infobox.latlon)) {
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
          '<a class="near" href="#NearFlights">Load nearby flights</a>' +
          '</div>'
          );

      get_near_flights.on('click touchend', function(e) {
        infobox.hide();
        getNearFlights(lon, lat, time, flight);
        visible = false;
      });

      return get_near_flights;
    };

    function locationInfo(lon, lat) {
      var get_location_info = $(
          '<div class="info-item">' +
          '<a class="near" href="#LocationInfo">Get location info</a>' +
          '</div>'
          );

      get_location_info.on('click touchend', function(e) {
        getLocationInfo(lon, lat);
      });

      return get_location_info;
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

      // make sure there's no other circle on the map
      var infobox_layer = map.getLayersByName('InfoBox')[0];
      infobox_layer.destroyFeatures(
          infobox_layer.getFeatureBy('renderIntent', 'nearestCircle')
      );

      circle = new OpenLayers.Feature.Vector(
          new OpenLayers.Geometry.Polygon.createRegularPolygon(point,
              distance_deg, 40, 0));

      // draw this circle and fade the inner fill within 500ms
      circle.renderIntent = 'nearestCircle';

      map.getLayersByName('InfoBox')[0].addFeatures(circle);

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
      $(circle_id).fadeOut(duration, function() {
        // check if circle still exists, because it might got deleted before
        // the animation was done.
        if (circle !== null) {
          var infobox_layer = map.getLayersByName('InfoBox')[0];
          infobox_layer.destroyFeatures(circle);
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
      var req = $.ajax('/flights/' + flight.sfid + '/near?lon=' + lon +
          '&lat=' + lat + '&time=' + time);

      req.done(function(data) {
        for (var i = 0; i < data.flights.length; ++i) {
          var flight = data.flights[i];

          // skip retrieved flight if already on map
          if (flights.has(flight.sfid))
            continue;

          var flight_id = addFlight(
              flight.sfid,
              flight.encoded.points,
              flight.encoded.levels,
              flight.num_levels,
              flight.barogram_t,
              flight.barogram_h,
              flight.enl,
              flight.zoom_levels,
              flight.contests,
              flight.additional);
        }
      });

      req.always(function() {
        hideCircle(1000);
      });
    };

    /**
     * Request location informations via ajax
     *
     * @param {Number} lon Longitude.
     * @param {Number} lat Latitude.
     */
    function getLocationInfo(lon, lat) {
      var req = $.ajax('/api/?lon=' + lon + '&lat=' + lat);

      req.done(function(data) {
        showLocationData(data);
      });

      req.fail(function() {
        showLocationData(null);
      });
    };

    /**
     * Show location data in infobox
     *
     * @param {Object} data Location data.
     */
    function showLocationData(data) {
      if (!visible) return; // do nothing if infobox is closed already

      infobox.empty();
      var item = $('<div class="location info-item"></div>');
      var no_data = true;

      if (data) {
        if (!$.isEmptyObject(data.airspaces) &&
            map.getLayersByName('Airspace')[0].visibility) {
          var p = $('<p></p>');
          p.append(formatAirspaceData(data.airspaces));
          item.append(p);
          no_data = false;
        }

        if (!$.isEmptyObject(data.waves) &&
            map.getLayersByName('Mountain Wave Project')[0].visibility) {
          var p = $('<p></p>');
          p.append(formatMountainWaveData(data.waves));
          item.append(p);
          no_data = false;
        }
      }

      if (no_data) {
        item.html('No data retrieved for this location');

        infobox.delay(1500).fadeOut(1000, function() {
          infobox.hide();
          visible = false;
        });

        hideCircle(1000);
      }

      infobox.append(item);

      pixel = map.getPixelFromLonLat(infobox.latlon);
      infobox.css('left', (pixel.x + 15) + 'px');
      infobox.css('top', (pixel.y - infobox.height() / 2) + 'px');
    };

    /**
     * Format Airspace data for infobox
     *
     * @param {Object} data Airspace data.
     */
    function formatAirspaceData(data) {
      var table = $('<table></table>');

      table.append($(
          '<thead><tr>' +
          '<th colspan="4">Airspaces</th>' +
          '</tr><tr>' +
          '<th>Name</th>' +
          '<th>Class</th>' +
          '<th>Base</th>' +
          '<th>Top</th>' +
          '</tr></thead>'
          ));

      var table_body = $('<tbody></tbody');

      for (var i = 0; i < data.length; ++i) {
        table_body.append($(
            '<tr>' +
            '<td class="airspace_name">' + data[i].name + '</td>' +
            '<td class="airspace_class">' + data[i].airspace_class + '</td>' +
            '<td class="airspace_base">' + data[i].base + '</td>' +
            '<td class="airspace_top">' + data[i].top + '</td>' +
            '</tr>'
            ));
      }

      table.append(table_body);

      return table;
    };


    /**
     * Format Mountain Wave data in infobox
     *
     * @param {Object} data Wave data.
     */
    function formatMountainWaveData(data) {
      var table = $('<table></table>');

      table.append($(
          '<thead><tr>' +
          '<th colspan="2">Mountain Waves</th>' +
          '</tr><tr>' +
          '<th>Name</th>' +
          '<th>Wind direction</th>' +
          '</tr></thead>'
          ));

      var table_body = $('<tbody></tbody');

      for (var i = 0; i < data.length; ++i) {
        table_body.append($(
            '<tr>' +
            '<td class="wave_name">' + data[i].name + '</td>' +
            '<td class="wave_direction">' +
                data[i].main_wind_direction +
            '°</td>' +
            '</tr>'
            ));
      }

      table.append(table_body);

      return table;
    };

  };
})();
