/**
 * This module handles the flight display page
 *
 * @constructor
 * @export
 * @param {ol.Map} map OpenLayers map object
 * @param {Ember.Component} fix_table
 * @param {Ember.Component} baro
 */
slFlightDisplay = function(map, fix_table, baro) {
  var flight_display = {};

  /**
   * Flight collection
   * @type {slFlightCollection}
   */
  var flights = slFlightCollection();
  var rawFlights = flights.getArray();

  /**
   * Handler for the plane icons
   * @type {slMapIconHandler}
   */
  var map_icon_handler = slMapIconHandler(map, rawFlights);

  /**
   * Handler for map hover events
   * @type {slMapHoverHandler}
   */
  var map_hover_handler = slMapHoverHandler(map, flights);

  var cesium_switcher;

  /**
   * Default time - the time to set when no time is set
   * @type {!Number}
   */
  var default_time = null;

  /**
   * List of colors for flight path display
   * @type {Array<String>}
   */
  var colors = ['#004bbd', '#bf0099', '#cf7c00',
                '#ff0000', '#00c994', '#ffff00'];

  /**
   * Initialize the map, add flight path and contest layers.
   */
  flight_display.init = function() {
    map_hover_handler.setMode(true);
    baro.set('hoverMode', true);

    cesium_switcher = new CesiumSwitcher();
    map.addControl(cesium_switcher);

    setupEvents();

    baro.set('flights', rawFlights);
    window.flightMap.set('flights', rawFlights);

    window.fixCalcService.set('flights', rawFlights);

    if (window.wingmanTable) {
      window.wingmanTable.set('visibleFlights', rawFlights);
    }
  };

  /**
   * Update the x-scale of the barogram
   */
  function updateBaroScale() {
    var extent = map.getView().calculateExtent(map.getSize());
    var interval = flights.getMinMaxTimeInExtent(extent);

    if (interval.max == -Infinity) {
      baro.set('timeInterval', null);
    } else {
      baro.set('timeInterval', [interval.min, interval.max]);
    }
  }


  /**
   * Add a flight to the map and barogram.
   *
   * @param {Object} data The data received from the JSON request.
   */
  flight_display.addFlight = function(data) {
    flight = slFlight.fromData(data);

    flight.set('color', colors[rawFlights.length % colors.length]);

    if (data.contests) {
      flight.set('contests', data.contests.map(function(data) {
        return slContest.fromData(data, flight.getID());
      }));
    }

    flights.add(flight);
  };


  /**
   * Perform a JSON request to get a flight.
   *
   * @param {String} url URL to fetch.
   * @param {Boolean=} opt_async do asynchronous request (defaults true)
   */
  flight_display.addFlightFromJSON = function(url, opt_async) {
    $.ajax(url, {
      async: (typeof opt_async === undefined) || opt_async === true,
      success: function(data) {
        if (rawFlights.findBy('id', data.sfid))
          return;

        flight_display.addFlight(data);
        map.render();
      }
    });
  };

  /**
   * Setup several events...
   */
  function setupEvents() {
    // Update the baro scale when the map has been zoomed/moved.
    var update_baro_scale_on_moveend = function(e) {
      updateBaroScale();
      baro.draw();
    };

    map.on('moveend', update_baro_scale_on_moveend);

    // Set the time when the mouse hoves the map
    $(map_hover_handler).on('set_time', function(e, time) {
      if (time) flight_display.setTime(time);
      else flight_display.setTime(default_time);
    });

    // Update the barogram when another flight has been selected
    // in the fix table.
    fix_table.addObserver('selection', function() {
      baro.set('selection', fix_table.get('selection'));
      baro.draw();
    });

    // Remove a flight when the removal button has been pressed
    // in the fix table.
    fix_table.on('remove_flight', function(sfid) {
      // never remove the first flight...
      if (Ember.get(rawFlights, 'firstObject.id') == sfid) return;
      flights.remove(sfid);
    });

    // Hide the plane icon of a flight which is scheduled for removal.
    $(flights).on('preremove', function(e, flight) {
      // Hide plane to remove any additional related objects from the map
      if (cesium_switcher.getMode()) {
        cesium_switcher.hidePlane(flight);
      } else {
        map_icon_handler.hidePlane(flight);
      }
    });

    // After a flight has been removed, remove highlights from the
    // wingman table, remove it from the fix table and update the barogram.
    $(flights).on('removed', function(e, sfid) {
      updateBaroScale();
      baro.draw();
    });

    // Add a flight to the fix table and barogram, highlight in the
    // wingman table.
    $(flights).on('add', function(e, flight) {
      updateBaroScale();
      baro.draw();
    });

    window.fixCalcService.addObserver('isRunning', function() {
      var running = this.get('isRunning');

      map_hover_handler.setMode(!running && !cesium_switcher.getMode());
      baro.set('hoverMode', !running);
    });

    // Add hover and click events to the barogram.
    baro.on('barohover', function(time) {
      flight_display.setTime(time);
    });
    baro.on('baroclick', function(time) {
      flight_display.setTime(time);
    });
    baro.on('mouseout', function() {
      flight_display.setTime(default_time);
    });

    $(cesium_switcher).on('cesium_enable', function(e) {
      map.un('moveend', update_baro_scale_on_moveend);

      if (!window.fixCalcService.get('isRunning')) {
        // disable mouse hovering
        map_hover_handler.setMode(false);
      }

      map_icon_handler.hideAllPlanes();

      map.getLayers().getArray().forEach(function(e) {
        if (e.get('name') == 'Contest') e.setVisible(false);
      });

      map.getLayers().getArray().forEach(function(e) {
        if (!e.get('base_layer') && !(e instanceof ol.layer.Vector))
          e.setVisible(false);
      });

      baro.set('timeInterval', null);
      baro.draw();
    });

    $(cesium_switcher).on('cesium_disable', function(e) {
      // Update the baro scale when the map has been zoomed/moved.
      map.on('moveend', update_baro_scale_on_moveend);

      if (!window.fixCalcService.get('isRunning')) {
        // enable mouse hovering
        map_hover_handler.setMode(true);
      }

      map.getLayers().getArray().forEach(function(e) {
        if (e.get('name') == 'Contest') e.setVisible(true);
      });
    });
  }


  /**
   * Set the current time.
   * @param {!Number} time Time to set
   */
  flight_display.setTime = function(time) {
    window.fixCalcService.set('time', time);
  };

  window.fixCalcService.addObserver('fixes.@each.point', function() {
    this.get('fixes').forEach(function(fix_data) {
      var flight = fix_data.get('flight');

      if (cesium_switcher.getMode()) {
        if (!fix_data.get('point')) {
          cesium_switcher.hidePlane(flight);
        } else {
          cesium_switcher.showPlane(flight, fix_data);
        }

      } else {
        if (!fix_data.get('point')) {
          map_icon_handler.hidePlane(flight);
        } else {
          map_icon_handler.showPlane(flight, fix_data);
        }
      }
    });
  });

  /**
   * Updates the barogram
   */
  flight_display.update = function() {
    updateBaroScale();
    baro.draw();
  };

  /**
   * Returns the flights collection
   * @return {slFlightCollection}
   */
  flight_display.getFlights = function() {
    return flights;
  };

  /**
   * Set the default time. Used at the tracking page.
   * @param {!Number} time Default time to set
   */
  flight_display.setDefaultTime = function(time) {
    default_time = time;
  };

  /**
   * Returns the barogram module
   * @return {slBarogram}
   */
  flight_display.getBaro = function() {
    return baro;
  };

  flight_display.init();
  return flight_display;
};
