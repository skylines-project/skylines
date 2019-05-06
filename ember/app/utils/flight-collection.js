import ArrayProxy from '@ember/array/proxy';

import ol from 'openlayers';

export default ArrayProxy.extend({
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
    return this.source.getExtent();
  },

  /**
   * Returns the minimum and maximum fix time within the extent.
   * Code based on ol.render.canvas.Replay.prototype.appendFlatCoordinates.
   * @param {ol.extent} extent
   * @return {Object}
   */
  getMinMaxTimeInExtent(extent) {
    let min = Infinity;
    let max = -Infinity;

    let total_min = Infinity;
    let total_max = -Infinity;

    this.source.forEachFeatureInExtent(extent, feature => {
      let coordinates = feature.getGeometry().getCoordinates();

      let lastCoord = coordinates[0];
      let nextCoord = null;
      let end = coordinates.length;

      let lastRel = ol.extent.containsCoordinate(extent, lastCoord);

      total_min = Math.min(total_min, lastCoord[3]);

      if (lastRel === true) {
        min = Math.min(lastCoord[3], min);
      }

      for (let i = 1; i < end; i += 1) {
        nextCoord = coordinates[i];

        let nextRel = ol.extent.containsCoordinate(extent, nextCoord);

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

      if (lastRel === true) {
        max = Math.max(lastCoord[3], max);
      }

      total_max = Math.max(total_max, lastCoord[3]);
    });

    if (min === Infinity) {
      min = total_min;
    }
    if (max === -Infinity) {
      max = total_max;
    }

    return { min, max };
  },

  arrayContentWillChange(offset, removeCount) {
    this._super(...arguments);

    let flights = this.content;
    let removedFlights = flights.slice(offset, offset + removeCount);

    let source = this.source;
    removedFlights.forEach(flight => {
      let id = flight.get('id');

      this.source
        .getFeatures()
        .filter(feature => feature.get('sfid') === id)
        .forEach(feature => source.removeFeature(feature));
    });
  },

  arrayContentDidChange(offset, removeCount, addCount) {
    let flights = this.content;
    let addedFlights = flights.slice(offset, offset + addCount);

    let source = this.source;
    addedFlights.forEach(flight => {
      let feature = new ol.Feature({
        geometry: flight.get('geometry'),
        sfid: flight.get('id'),
        color: flight.get('color'),
        type: 'flight',
      });

      source.addFeature(feature);
    });

    this._super(...arguments);
  },
});
