/* globals $ */

import Ember from 'ember';
import ol from 'openlayers';

import slFlight from './flight';
import slFlightCollection from './flight-collection';
import slMapHoverHandler from './map-hover-handler';
import CesiumSwitcher from './cesium-switcher';

/**
 * List of colors for flight path display
 * @type {Array<String>}
 */
const COLORS = [
  '#004bbd',
  '#bf0099',
  '#cf7c00',
  '#ff0000',
  '#00c994',
  '#ffff00',
];

/**
 * This module handles the flight display page
 *
 * @constructor
 * @export
 * @param {ol.Map} map OpenLayers map object
 * @param {Ember.Component} fix_table
 * @param {Ember.Component} baro
 */
export default function slFlightDisplay(map, fix_table, baro) {
  var flight_display = {};

  /**
   * Flight collection
   * @type {slFlightCollection}
   */
  var flights = slFlightCollection.create();

  /**
   * Handler for map hover events
   * @type {slMapHoverHandler}
   */
  var map_hover_handler = slMapHoverHandler.create({
    map: map,
    flights: flights,
  });

  var cesium_switcher;

  /**
   * Default time - the time to set when no time is set
   * @type {!Number}
   */
  var default_time = null;

  /**
   * Initialize the map, add flight path and contest layers.
   */
  flight_display.init = function() {
    map_hover_handler.set('hover_enabled', true);
    baro.set('hoverMode', true);

    cesium_switcher = CesiumSwitcher.create();
    map.addControl(cesium_switcher);

    setupEvents();

    baro.set('flights', flights);
    window.flightMap.set('flights', flights);

    window.fixCalcService.set('flights', flights);

    if (window.wingmanTable) {
      window.wingmanTable.set('visibleFlights', flights);
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
    let flight = slFlight.fromData(data);

    flight.set('color', COLORS[flights.get('length') % COLORS.length]);

    flights.pushObject(flight);
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
        if (flights.findBy('id', data.sfid))
          return;

        flight_display.addFlight(data);
        map.render();
      },
    });
  };

  /**
   * Setup several events...
   */
  function setupEvents() {
    // Update the baro scale when the map has been zoomed/moved.
    var update_baro_scale_on_moveend = function() {
      updateBaroScale();
      baro.draw();
    };

    map.on('moveend', update_baro_scale_on_moveend);

    // Set the time when the mouse hoves the map
    map_hover_handler.on('set_time', function(time) {
      if (time) flight_display.setTime(time);
      else flight_display.setTime(default_time);
    });

    // Update the barogram when another flight has been selected
    // in the fix table.
    fix_table.addObserver('selection', function() {
      baro.set('selection', fix_table.get('selection'));
      Ember.run.once(baro, 'draw');
    });

    // Remove a flight when the removal button has been pressed
    // in the fix table.
    fix_table.on('remove_flight', function(sfid) {
      // never remove the first flight...
      if (Ember.get(flights, 'firstObject.id') == sfid) return;

      flights.removeObjects(flights.filterBy('id', sfid));
    });

    // Hide the plane icon of a flight which is scheduled for removal.
    flights.addArrayObserver({
      arrayWillChange: function(flights, offset, removeCount) {
        flights.slice(offset, offset + removeCount).forEach(function(flight) {
          // Hide plane to remove any additional related objects from the map
          if (cesium_switcher.getMode()) {
            cesium_switcher.hidePlane(flight);
          }
        });
      },
      arrayDidChange: Ember.K,
    });

    flights.addObserver('[]', function() {
      Ember.run.once(flight_display, 'update');
    });

    window.fixCalcService.addObserver('isRunning', function() {
      var running = this.get('isRunning');

      map_hover_handler.set('hover_enabled', !running && !cesium_switcher.getMode());
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

    cesium_switcher.addObserver('enabled', function() {
      let enabled = this.get('enabled');
      window.flightMap.set('cesiumEnabled', enabled);

      if (enabled) {
        map.un('moveend', update_baro_scale_on_moveend);

        if (!window.fixCalcService.get('isRunning')) {
          // disable mouse hovering
          map_hover_handler.set('hover_enabled', false);
        }

        map.getLayers().getArray().forEach(function(e) {
          if (e.get('name') == 'Contest') e.setVisible(false);
        });

        map.getLayers().getArray().forEach(function(e) {
          if (!e.get('base_layer') && !(e instanceof ol.layer.Vector))
            e.setVisible(false);
        });

        baro.set('timeInterval', null);
        baro.draw();

      } else {
        // Update the baro scale when the map has been zoomed/moved.
        map.on('moveend', update_baro_scale_on_moveend);

        if (!window.fixCalcService.get('isRunning')) {
          // enable mouse hovering
          map_hover_handler.set('hover_enabled', true);
        }

        map.getLayers().getArray().forEach(function(e) {
          if (e.get('name') == 'Contest') e.setVisible(true);
        });
      }
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
}
