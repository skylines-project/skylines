/**
 * This module handles the flight display page
 *
 * @constructor
 * @export
 * @param {ol.Map} _map OpenLayers map object
 * @param {jQuery} fix_table_placeholder Placeholder for the fix table
 * @param {jQuery} baro_placeholder Placeholder for the barogram
 */
slFlightDisplay = function(_map, fix_table_placeholder, baro_placeholder) {
  var flight_display = {};
  var map = _map;

  /**
   * Flight collection
   * @type {slFlightCollection}
   */
  var flights = slFlightCollection();

  /**
   * Contest collection
   * @type {slContestCollection}
   */
  var contests = slContestCollection();

  /**
   * Fix table module
   * @type {slFixTable}
   */
  var fix_table = slFixTable(fix_table_placeholder);

  /**
   * Handler for the plane icons and map hover events
   * @type {slMapIconHandler}
   */
  var map_icon_handler = slMapIconHandler(map, flights);

  /**
   * Barogram module
   * @type {slBarogram}
   */
  var baro = slBarogram(baro_placeholder);

  /**
   * Play button control
   * @type {PlayButton}
   */
  var play_button;

  var cesium_switcher;

  /**
   * Default time - the time to set when no time is set
   * @type {!Number}
   */
  var default_time = null;

  /*
   * Global time, can be:
   * null -> no time is set, don't show barogram crosshair/plane position
   * -1 -> always show the latest time/fix for each flight
   * >= 0 -> show the associated time in the barogram and on the map
   * @type {!Number}
   */
  var global_time = default_time;


  /**
   * List of colors for flight path display
   * @type {Array<String>}
   */
  var colors = ['#004bbd', '#bf0099', '#cf7c00',
                '#ff0000', '#00c994', '#ffff00'];


  /**
   * Determin the drawing style for the feature
   * @param {ol.feature} feature Feature to style
   * @return {!Array<ol.style.Style>} Style of the feature
   */
  function style_function(feature) {
    if (!$.inArray('type', feature.getKeys()))
      return null;

    var color = '#004bbd'; // default color
    if ($.inArray('color', feature.getKeys()))
      color = feature.get('color');

    var z_index = 1000; // default z-index
    var line_dash = undefined; // default line style

    switch (feature.get('type')) {
      case 'flight':
        z_index = 1000;
        break;

      case 'contest':
        z_index = 999;
        line_dash = [5];
        break;
    }

    return [new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: color,
        width: 2,
        lineDash: line_dash
      }),
      zIndex: z_index
    })];
  }


  /**
   * Initialize the map, add flight path and contest layers.
   * Adds the PlayButton to the map and activates all hover modes.
   */
  flight_display.init = function() {
    //var flight_path_layer = new ol.layer.Image({
    //  source: new ol.source.ImageVector({
    //    source: flights.getSource(),
    //    style: style_function
    //  }),
    var flight_path_layer = new ol.layer.Vector({
      source: flights.getSource(),
      style: style_function,
      name: 'Flight',
      zIndex: 50
    });

    map.addLayer(flight_path_layer);

    var flight_contest_layer = new ol.layer.Vector({
      source: contests.getSource(),
      style: style_function,
      name: 'Contest',
      zIndex: 49
    });

    map.addLayer(flight_contest_layer);

    play_button = new PlayButton();
    map.addControl(play_button);

    map_icon_handler.setMode(true);
    baro.setHoverMode(true);

    cesium_switcher = new CesiumSwitcher();
    map.addControl(cesium_switcher);

    setupEvents();
  };

  /**
   * Update the x-scale of the barogram
   * @return {Boolean} True if the barogram should be redrawn
   */
  function updateBaroScale() {
    var extent = map.getView().calculateExtent(map.getSize());
    var interval = flights.getMinMaxTimeInExtent(extent);

    var redraw = false;

    if (interval.max == -Infinity) {
      baro.clearTimeInterval();
      redraw = true;
    } else {
      redraw = baro.setTimeInterval(interval.min, interval.max);
    }

    return redraw;
  }


  /**
   * Add a flight to the map and barogram.
   *
   * @param {Object} data The data received from the JSON request.
   */
  flight_display.addFlight = function(data) {
    flight = slFlight(data.sfid, data.points,
                      data.barogram_t, data.barogram_h,
                      data.enl,
                      data.elevations_t, data.elevations_h,
                      data.geoid, data.additional);

    flight.setColor(data.additional.color ||
                    colors[flights.length() % colors.length]);

    if (data.contests) {
      var _contestsLength = data.contests.length;
      for (var i = 0; i < _contestsLength; ++i)
        contests.add(slContest(data.contests[i], flight.getID()));
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
        if (flights.has(data.sfid))
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
      if (updateBaroScale())
        baro.draw();
    };

    map.on('moveend', update_baro_scale_on_moveend);

    // Set the time when the mouse hoves the map
    $(map_icon_handler).on('set_time', function(e, time) {
      if (time) flight_display.setTime(time);
      else flight_display.setTime(default_time);
    });

    // Update the barogram when another flight has been selected
    // in the fix table.
    $(fix_table).on('selection_changed', function(e) {
      updateBaroData();
      baro.draw();
    });

    // Remove a flight when the removal button has been pressed
    // in the fix table.
    $(fix_table).on('remove_flight', function(e, sfid) {
      // never remove the first flight...
      if (flights.at(0).getID() == sfid) return;
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
      $('#wingman-table').find('*[data-sfid=' + sfid + ']')
          .find('.color-stripe').css('background-color', '');

      contests.remove(sfid);
      fix_table.removeRow(sfid);
      updateBaroData();
      updateBaroScale();
      baro.draw();
    });

    // Add a flight to the fix table and barogram, highlight in the
    // wingman table.
    $(flights).on('add', function(e, flight) {
      // Add flight as a row to the fix data table
      fix_table.addRow(flight.getID(), flight.getColor(),
                       flight.getCompetitionID());

      updateBaroData();
      updateBaroScale();
      baro.draw();

      $('#wingman-table').find('*[data-sfid=' + flight.getID() + ']')
          .find('.color-stripe').css('background-color', flight.getColor());

      // Set fix data table into "selectable" mode if
      // more than one flight is loaded
      if (flights.length() > 1)
        fix_table.setSelectable(true);

      flight_display.setTime(global_time);
    });

    // Disable hover modes for map and barogram when the play button
    // has been pressed. Determine the start time for playing.
    $(play_button).on('play', function(e) {
      // if there are no flights, then there is nothing to animate
      if (flights.length == 0)
        return false;

      // if no time is set
      if (global_time == null || global_time == -1) {
        // find the first timestamp of all flights
        var start_time = Number.MAX_VALUE;
        flights.each(function(flight) {
          if (flight.getStartTime() < start_time)
            start_time = flight.getStartTime();
        });

        // start the animation at the beginning
        flight_display.setTime(start_time);
      }

      // disable mouse hovering
      map_icon_handler.setMode(false);
      baro.setHoverMode(false);

      return true;
    });

    // Enable hover modes after stopping replay.
    $(play_button).on('stop', function(e) {
      // reenable mouse hovering
      if (!cesium_switcher.getMode()) map_icon_handler.setMode(true);
      baro.setHoverMode(true);
    });

    // Advance time on replay tick.
    $(play_button).on('tick', function(e) {
      // increase time
      var time = global_time + 1;

      // find the last timestamp of all flights
      var stop_time = Number.MIN_VALUE;
      flights.each(function(flight) {
        if (flight.getEndTime() > stop_time)
          stop_time = flight.getEndTime();
      });

      // check if we are at the end of the animation
      if (time > stop_time) {
        stop();
        return false;
      }

      // set the time for the new animation frame
      flight_display.setTime(time);

      return true;
    });

    // Add hover and click events to the barogram.
    $(baro).on('barohover', function(event, time) {
      flight_display.setTime(time);
    }).on('baroclick', function(event, time) {
      flight_display.setTime(time);
    }).on('mouseout', function(event) {
      flight_display.setTime(default_time);
    });

    $(cesium_switcher).on('cesium_enable', function(e) {
      map.un('moveend', update_baro_scale_on_moveend);

      if (!play_button.getMode()) {
        // disable mouse hovering
        map_icon_handler.setMode(false);
      }

      map_icon_handler.hideAllPlanes();

      map.getLayers().getArray().forEach(function(e) {
        if (e.get('name') == 'Contest') e.setVisible(false);
      });

      map.getLayers().getArray().forEach(function(e) {
        if (!e.get('base_layer') && !(e instanceof ol.layer.Vector))
          e.setVisible(false);
      });

      baro.clearTimeInterval();
      baro.draw();
    });

    $(cesium_switcher).on('cesium_disable', function(e) {
      // Update the baro scale when the map has been zoomed/moved.
      map.on('moveend', update_baro_scale_on_moveend);

      if (!play_button.getMode()) {
        // enable mouse hovering
        map_icon_handler.setMode(true);
      }

      map.getLayers().getArray().forEach(function(e) {
        if (e.get('name') == 'Contest') e.setVisible(true);
      });
    });
  }

  /**
   * Update the data to be displayed in the barogram
   */
  function updateBaroData() {
    var _contests = [], elevations = [];

    var active = [], passive = [], enls = [];
    flights.each(function(flight) {
      var data = {
        data: flight.getFlotHeight(),
        color: flight.getColor()
      };

      var enl_data = {
        data: flight.getFlotENL(),
        color: flight.getColor()
      };

      if (fix_table.getSelection() &&
          flight.getID() != fix_table.getSelection()) {
        passive.push(data);
      } else {
        active.push(data);
        enls.push(enl_data);
      }

      // Save contests of highlighted flight for later
      if (fix_table.getSelection() &&
          flight.getID() == fix_table.getSelection()) {
        _contests = contests.all(flight.getID());
        elevations = flight.getFlotElev();
      }

      // Save contests of only flight for later if applicable
      if (flights.length() == 1) {
        _contests = contests.all(flight.getID());
        elevations = flight.getFlotElev();
      }
    });

    baro.setActiveTraces(active);
    baro.setPassiveTraces(passive);
    baro.setENLData(enls);
    baro.setContests(_contests);
    baro.setElevations(elevations);
  }

  /**
   * Set the current time.
   * @param {!Number} time Time to set
   */
  flight_display.setTime = function(time) {
    global_time = time;

    // if the mouse is not hovering over the barogram or any trail on the map
    if (!time) {
      // remove crosshair from barogram
      baro.clearTime();

      // remove plane icons from map
      if (cesium_switcher.getMode()) {
        flights.each(function(flight) {
          cesium_switcher.hidePlane(flight);
        });
      } else {
        map_icon_handler.hideAllPlanes();
      }

      // remove data from fix-data table
      fix_table.clearAllFixes();

    } else {
      // update barogram crosshair
      baro.setTime(time);

      flights.each(function(flight) {
        // calculate fix data
        var fix_data = flight.getFixData(time);
        if (!fix_data) {
          // update map
          if (cesium_switcher.getMode()) {
            cesium_switcher.hidePlane(flight);
          } else {
            map_icon_handler.hidePlane(flight);
          }

          // update fix-data table
          fix_table.clearFix(flight.getID());
        } else {
          // update map
          if (cesium_switcher.getMode()) {
            cesium_switcher.showPlane(flight, fix_data);
          } else {
            map_icon_handler.showPlane(flight, fix_data);
          }

          // update fix-data table
          fix_table.updateFix(flight.getID(), fix_data);
        }
      });
    }

    map.render();
    fix_table.render();
  };

  /**
   * Updates the barogram
   */
  flight_display.update = function() {
    updateBaroData();
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
   * Returns the current global time.
   * @return {!Number}
   */
  flight_display.getGlobalTime = function() {
    return global_time;
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
