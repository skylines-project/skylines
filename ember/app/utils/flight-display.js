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

  // Update the barogram when another flight has been selected
  // in the fix table.
  fixTableObserver: Ember.observer('fix_table.selection', function() {
    let baro = this.get('baro');
    baro.set('selection', this.get('fix_table.selection'));
    Ember.run.once(baro, 'draw');
  }),

  baro: null,

  /**
   * Flight collection
   * @type {slFlightCollection}
   */
  flights: Ember.computed.readOnly('fixCalc.flights'),

  flightsObserver: Ember.observer('flights.[]', function() {
    Ember.run.once(this, 'update');
  }),

  /**
   * Handler for map hover events
   * @type {slMapHoverHandler}
   */
  map_hover_handler: null,

  cesiumEnabled: Ember.computed.readOnly('flightMap.cesiumEnabled'),

  cesiumObserver: Ember.observer('cesiumEnabled', function() {
    let map = this.get('map');
    let update_baro_scale_on_moveend = this.get('update_baro_scale_on_moveend');

    if (this.get('cesiumEnabled')) {
      map.un('moveend', update_baro_scale_on_moveend);

      map.getLayers().getArray().forEach(function(e) {
        if (!e.get('base_layer') && !(e instanceof ol.layer.Vector))
          e.setVisible(false);
      });

      let baro = this.get('baro');

      baro.set('timeInterval', null);
      baro.draw();

    } else {
      // Update the baro scale when the map has been zoomed/moved.
      map.on('moveend', update_baro_scale_on_moveend);
    }
  }),

  /**
   * Initialize the map, add flight path and contest layers.
   */
  init() {
    let map = this.get('map');

    this.set('map_hover_handler', slMapHoverHandler.create({
      fixCalc: this.get('fixCalc'),
      flightMap: this.get('flightMap'),
    }));

    // Update the baro scale when the map has been zoomed/moved.
    let update_baro_scale_on_moveend = () => this.update();
    this.set('update_baro_scale_on_moveend', update_baro_scale_on_moveend);

    map.on('moveend', update_baro_scale_on_moveend);
  },

  /**
   * Update the x-scale of the barogram
   */
  updateBaroScale() {
    let map = this.get('map');
    let baro = this.get('baro');
    let flights = this.get('flights');

    let extent = map.getView().calculateExtent(map.getSize());
    let interval = flights.getMinMaxTimeInExtent(extent);

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
});
