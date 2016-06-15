/* globals ol */

import Ember from 'ember';

export default Ember.ArrayProxy.extend({

  init() {
    this.set('content', []);
    this.set('source', new ol.source.Vector());

    this._super(...arguments);
  },

  /**
   * Calculates the bounds of all flights in the collection.
   * @return {ol.extent}
   */
  getBounds() {
    return this.get('source').getExtent();
  },

  /**
   * Returns the vector layer source of this collection.
   * @return {ol.source.Vector}
   */
  getSource() {
    return this.get('source');
  },

  /**
   * Returns the minimum and maximum fix time within the extent.
   * Code based on ol.render.canvas.Replay.prototype.appendFlatCoordinates.
   * @param {ol.extent} extent
   * @return {Object}
   */
  getMinMaxTimeInExtent(extent) {
    var min = Infinity,
      total_min = Infinity;
    var max = -Infinity,
      total_max = -Infinity;

    this.get('source').forEachFeatureInExtent(extent, function(f) {
      var coordinates = f.getGeometry().getCoordinates();

      var lastCoord = coordinates[0];
      var nextCoord = null;
      var end = coordinates.length;

      var lastRel = ol.extent.containsCoordinate(extent, lastCoord),
        nextRel;

      total_min = Math.min(total_min, lastCoord[3]);

      if (lastRel == true)
        min = Math.min(lastCoord[3], min);

      for (var i = 1; i < end; i += 1) {
        nextCoord = coordinates[i];

        nextRel = ol.extent.containsCoordinate(extent, nextCoord);

        // current vector completely within extent. do nothing.
        // current vector completely outside extent. do nothing.

        // last vertice was inside extent, next one is outside.
        if (lastRel && !nextRel) {
          max = Math.max(nextCoord[3], max);
          lastRel = nextRel;
        } else if (!lastRel && nextRel) {
          // last vertice was outside extent, next one is inside
          min = Math.min(lastCoord[3], min);
        }

        lastCoord = nextCoord;
        lastRel = nextRel;
      }

      if (lastRel == true)
        max = Math.max(lastCoord[3], max);

      total_max = Math.max(total_max, lastCoord[3]);
    });

    if (min == Infinity) min = total_min;
    if (max == -Infinity) max = total_max;

    return { min: min, max: max };
  },

  contentArrayWillChange(flights, offset, removeCount) {
    let source = this.get('source');

    flights.slice(offset, offset + removeCount).forEach(function(flight) {
      source.removeFeature(source.getFeatures().filter(function(it) {
        return it.get('sfid') == flight.getID();
      })[0]);
    });
  },

  contentArrayDidChange(flights, offset, removeCount, addCount) {
    let source = this.get('source');

    flights.slice(offset, offset + addCount).forEach(function(flight) {
      var feature = new ol.Feature({
        geometry: flight.get('geometry'),
        sfid: flight.get('id'),
        color: flight.get('color'),
        type: 'flight',
      });

      source.addFeature(feature);
    });
  },
});
