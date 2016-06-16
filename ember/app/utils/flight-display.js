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
export default Ember.Object.extend({
  fixCalc: null,
  flightMap: null,

  map: Ember.computed.readOnly('flightMap.map'),
  fix_table: null,
  baro: null,

  /**
   * Flight collection
   * @type {slFlightCollection}
   */
  flights: Ember.computed.readOnly('fixCalc.flights'),

  /**
   * Handler for map hover events
   * @type {slMapHoverHandler}
   */
  map_hover_handler: null,

  /**
   * Initialize the map, add flight path and contest layers.
   */
  init() {
    let map = this.get('map');
    let fix_table = this.get('fix_table');
    let baro = this.get('baro');
    let flights = this.get('flights');

    let map_hover_handler = slMapHoverHandler.create({
      fixCalc: this.get('fixCalc'),
      flightMap: this.get('flightMap'),
    });
    this.set('map_hover_handler', map_hover_handler);

    // Update the baro scale when the map has been zoomed/moved.
    var update_baro_scale_on_moveend = () => {
      this.updateBaroScale();
      baro.draw();
    };

    map.on('moveend', update_baro_scale_on_moveend);

    // Set the time when the mouse hoves the map
    map_hover_handler.on('set_time', time => {
      if (time) {
        this.get('fixCalc').set('time', time);
      } else {
        this.get('fixCalc').resetTime();
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

    flights.addObserver('[]', () => {
      Ember.run.once(this, 'update');
    });

    // Add hover and click events to the barogram.
    baro.on('barohover', time => {
      this.get('fixCalc').set('time', time);
    });
    baro.on('baroclick', time => {
      this.get('fixCalc').set('time', time);
    });
    baro.on('mouseout', () => {
      this.get('fixCalc').resetTime();
    });

    this.get('flightMap').addObserver('cesiumEnabled', function() {
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
  },

  /**
   * Update the x-scale of the barogram
   */
  updateBaroScale() {
    let map = this.get('map');
    let baro = this.get('baro');
    let flights = this.get('flights');

    var extent = map.getView().calculateExtent(map.getSize());
    var interval = flights.getMinMaxTimeInExtent(extent);

    if (interval.max == -Infinity) {
      baro.set('timeInterval', null);
    } else {
      baro.set('timeInterval', [interval.min, interval.max]);
    }
  },

  /**
   * Updates the barogram
   */
  update() {
    this.updateBaroScale();
    this.get('baro').draw();
  },

  /**
   * Returns the flights collection
   * @return {slFlightCollection}
   */
  getFlights() {
    return this.get('flights');
  },
});
