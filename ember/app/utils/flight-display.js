import Ember from 'ember';

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

  /**
   * Handler for map hover events
   * @type {slMapHoverHandler}
   */
  map_hover_handler: null,

  /**
   * Initialize the map, add flight path and contest layers.
   */
  init() {
    this.set('map_hover_handler', slMapHoverHandler.create({
      fixCalc: this.get('fixCalc'),
      flightMap: this.get('flightMap'),
    }));
  },
});
