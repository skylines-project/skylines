/**
 * @constructor
 * @param {ol.Map} map Openlayers map instance
 * @param {slFlightDisplay} flight_display Flight display module
 * @param {Object} settings Settings for this module
 */
slMapClickHandler = function(map, flight_display, settings) {
  var map_click_handler = {};

  // Private attributes

  /**
   * The OpenLayers.Geometry object of the circle.
   * @type {Object}
   */
  var circle = { geometry: null, animation: null };

  /**
   * Stores the state if the infobox.
   * @type {Boolean}
   */
  var visible = false;


  var infobox = null;

  // Public attributes and functions

  /**
   * Click handler which shows a info box at the click location.
   *
   * @this {ol.Map}
   * @param {Event} e
   * @return {(boolean|undefined)}
   */
  map_click_handler.trigger = function(e) {
    // Hide infobox if it's currently visible
    if (visible) {
      e.map.removeOverlay(infobox);
      hideCircle(0);
      visible = false;
      infobox = null;
      return;
    }

    if (!infobox) {
      infobox = new ol.Overlay({
        element: $("<div id='MapInfoBox' class='InfoBox'></div>")
      });
    }

    var infobox_element = infobox.getElement();
    var coordinate = e.coordinate;

    if (settings['flight_info'] && flight_display) {
      var flight_path_source = flight_display.getFlights().getSource();
      var closest_feature = flight_path_source
          .getClosestFeatureToCoordinate(coordinate);

      if (closest_feature !== null) {
        var geometry = closest_feature.getGeometry();
        var closest_point = geometry.getClosestPoint(coordinate);

        var feature_pixel = e.map.getPixelFromCoordinate(closest_point);
        var mouse_pixel = e.map.getPixelFromCoordinate(coordinate);

        var squared_distance = Math.pow(mouse_pixel[0] - feature_pixel[0], 2) +
                               Math.pow(mouse_pixel[1] - feature_pixel[1], 2);

        if (squared_distance < 100) {
          var time = closest_point[3];
          var sfid = closest_feature.get('sfid');
          var flight = flight_display.getFlights().get(sfid);

          // flight info
          var flight_info = flightInfo(flight);
          infobox_element.append(flight_info);

          // near flights link
          var loc = ol.proj.transform(closest_point,
                                      'EPSG:3857',
                                      'EPSG:4326');
          var get_near_flights = nearFlights(loc[0], loc[1], time, flight);
          infobox_element.append(get_near_flights);

          coordinate = closest_point;
        }
      }
    }

    if (settings['location_info']) {
      // location info
      var loc = ol.proj.transform(coordinate, 'EPSG:3857', 'EPSG:4326');
      var get_location_info = locationInfo(loc[0], loc[1]);
      infobox_element.append(get_location_info);
    }

    e.map.addOverlay(infobox);
    infobox.setPosition(coordinate);
    showCircle(coordinate);

    visible = true;

    return false; // stop bubbeling
  };

  map_click_handler.init = function() {
    map.on('click', map_click_handler.trigger);
  };

  map_click_handler.init();
  return map_click_handler;

  // Private functions

  /**
   * Returns the flight badge element
   * @param {slFlight} flight Flight object
   * @return {jQuery}
   */
  function flightInfo(flight) {
    return $(
        '<span class="info-item badge" style="background:' +
            flight.getColor() +
        '">' +
        (flight.getRegistration() || '') +
        '</span>'
    );
  }

  function nearFlights(lon, lat, time, flight) {
    var get_near_flights = $(
        '<div class="info-item">' +
        '<a class="near" href="#NearFlights">Load nearby flights</a>' +
        '</div>'
        );

    get_near_flights.on('click touchend', function(e) {
      map.removeOverlay(infobox);
      getNearFlights(lon, lat, time, flight);
      visible = false;
      infobox = null;
      e.preventDefault();
    });

    return get_near_flights;
  }

  function locationInfo(lon, lat) {
    var get_location_info = $(
        '<div class="info-item">' +
        '<a class="near" href="#LocationInfo">Get location info</a>' +
        '</div>'
        );

    get_location_info.on('click touchend', function(e) {
      getLocationInfo(lon, lat);
      e.preventDefault();
    });

    return get_location_info;
  }

  /**
   * Show a circle at the clicked position
   *
   * @param {Array<Number>} coordinate Coordinate
   */
  function showCircle(coordinate) {
    var stroke_style = new ol.style.Stroke({
      color: '#f4bd33',
      width: 3
    });

    /*
    var fill_style = new ol.style.Fill({
      opacity: 0.5,
      color: '#f4bd00'
    });
    */

    if (!circle.geometry)
      circle.geometry = new ol.geom.Circle(coordinate, 1000);
    else
      circle.geometry.setCenterAndRadius(coordinate, 1000);

    circle.animation = null;

    map.on('postcompose', function(e) {
      var vector_context = e.vectorContext;

      if (circle.geometry) {
        if (circle.animation != null) {
          var frame_state = e.frameState;
          if (!circle.animation.start)
            circle.animation.start = frame_state.time;

          if (circle.animation.duration <= 0 ||
              frame_state.time >
              circle.animation.start + circle.animation.duration) {
            circle.geometry = null;
            return;
          }

          var delta_time = -(circle.animation.start - frame_state.time) %
                           circle.animation.duration;
          stroke_style.setWidth(3 - delta_time /
                                (circle.animation.duration / 3));
        }

        vector_context.setFillStrokeStyle(null, stroke_style);
        vector_context.drawCircleGeometry(circle.geometry);
        map.render();
      }
    });
  }

  /**
   * Hides the search circle
   *
   * @param {Number} duration Fade duration in ms
   */
  function hideCircle(duration) {
    circle.animation = { duration: duration, start: null };
  }

  /**
   * Request near flights via ajax
   *
   * @param {Number} lon Longitude.
   * @param {Number} lat Latitude.
   * @param {Number} time Time.
   * @param {slFlight} flight Flight.
   */
  function getNearFlights(lon, lat, time, flight) {
    if (!flight_display) return;

    var req = $.ajax('/flights/' + flight.getID() + '/near?lon=' + lon +
        '&lat=' + lat + '&time=' + time);

    req.done(function(data) {
      for (var i = 0; i < data['flights'].length; ++i) {
        var flight = data['flights'][i];

        // skip retrieved flight if already on map
        if (flight_display.getFlights().has(flight['sfid']))
          continue;

        flight_display.addFlight(flight);
      }
    });

    req.always(function() {
      hideCircle(1000);
    });
  }

  /**
   * Request location informations via ajax
   *
   * @param {Number} lon Longitude.
   * @param {Number} lat Latitude.
   */
  function getLocationInfo(lon, lat) {
    var req = $.ajax(settings.api_url + '/mapitems?lon=' + lon + '&lat=' + lat);

    req.done(function(data) {
      showLocationData(data);
    });

    req.fail(function() {
      showLocationData(null);
    });
  }

  /**
   * Show location data in infobox
   *
   * @param {Object} data Location data.
   */
  function showLocationData(data) {
    if (!visible) return; // do nothing if infobox is closed already

    infobox.getElement().empty();
    var item = $('<div class="location info-item"></div>');
    var no_data = true;

    if (data) {
      var airspace_layer = map.getLayers().getArray().filter(function(e) {
        return e.get('name') == 'Airspace';
      })[0];
      var mwp_layer = map.getLayers().getArray().filter(function(e) {
        return e.get('name') == 'Mountain Wave Project';
      })[0];

      if (!$.isEmptyObject(data['airspaces']) &&
          airspace_layer.getVisible()) {
        var p = $('<p></p>');
        p.append(formatAirspaceData(data['airspaces']));
        item.append(p);
        no_data = false;
      }

      if (!$.isEmptyObject(data['waves']) &&
          mwp_layer.getVisible()) {
        var p = $('<p></p>');
        p.append(formatMountainWaveData(data['waves']));
        item.append(p);
        no_data = false;
      }
    }

    if (no_data) {
      item.html('No data retrieved for this location');

      infobox.getElement().delay(1500).fadeOut(1000, function() {
        map.removeOverlay(infobox);
        visible = false;
      });

      hideCircle(1000);
    }

    infobox.getElement().append(item);

    //infobox.setOffset([15, infobox.getElement().height() / 2]);
  }

  /**
   * Format Airspace data for infobox
   *
   * @param {Object} data Airspace data.
   * @return {jQuery} HTML table with the airspace data.
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
          '<td class="airspace_name">' + data[i]['name'] + '</td>' +
          '<td class="airspace_class">' + data[i]['class'] + '</td>' +
          '<td class="airspace_base">' + data[i]['base'] + '</td>' +
          '<td class="airspace_top">' + data[i]['top'] + '</td>' +
          '</tr>'
          ));
    }

    table.append(table_body);

    return table;
  }

  /**
   * Format Mountain Wave data in infobox
   *
   * @param {Object} data Wave data.
   * @return {jQuery} HTML table with the wave data.
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
      var wind_direction = data[i]['main_wind_direction'] || 'Unknown';

      table_body.append($(
          '<tr>' +
          '<td class="wave_name">' + data[i]['name'] + '</td>' +
          '<td class="wave_direction">' + wind_direction + '</td>' +
          '</tr>'
          ));
    }

    table.append(table_body);

    return table;
  }
};
