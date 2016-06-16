import Ember from 'ember';
import ol from 'openlayers';

import slMapHoverHandler from './map-hover-handler';

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
  var flights = window.fixCalcService.get('flights');

  /**
   * Handler for map hover events
   * @type {slMapHoverHandler}
   */
  var map_hover_handler = slMapHoverHandler.create({
    fixCalc: window.fixCalcService,
    flightMap: window.flightMap,
  });

  /**
   * Initialize the map, add flight path and contest layers.
   */
  flight_display.init = function() {
    setupEvents();
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
      if (time) {
        window.fixCalcService.set('time', time);
      } else {
        window.fixCalcService.resetTime();
      }
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

    flights.addObserver('[]', function() {
      Ember.run.once(flight_display, 'update');
    });

    // Add hover and click events to the barogram.
    baro.on('barohover', function(time) {
      window.fixCalcService.set('time', time);
    });
    baro.on('baroclick', function(time) {
      window.fixCalcService.set('time', time);
    });
    baro.on('mouseout', function() {
      window.fixCalcService.resetTime();
    });

    window.flightMap.addObserver('cesiumEnabled', function() {
      if (this.get('cesiumEnabled')) {
        map.un('moveend', update_baro_scale_on_moveend);

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

        map.getLayers().getArray().forEach(function(e) {
          if (e.get('name') == 'Contest') e.setVisible(true);
        });
      }
    });
  }


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

  flight_display.init();
  return flight_display;
}
