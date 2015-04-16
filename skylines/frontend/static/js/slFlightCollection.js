/**
 * An ordered collection of flight objects.
 * @constructor
 */
slFlightCollection = function() {
  var collection = slCollection();

  // Public attributes and methods

  var source = new ol.source.Vector();

  /**
   * Calculates the bounds of all flights in the collection.
   * @return {ol.extent}
   */
  collection.getBounds = function() {
    return source.getExtent();
  };

  /**
   * Returns the vector layer source of this collection.
   * @return {ol.source.Vector}
   */
  collection.getSource = function() {
    return source;
  };

  /**
   * Returns the minimum and maximum fix time within the extent.
   * Code based on ol.render.canvas.Replay.prototype.appendFlatCoordinates.
   * @param {ol.extent} extent
   * @return {Object}
   */
  collection.getMinMaxTimeInExtent = function(extent) {
    var min = Infinity,
        total_min = Infinity;
    var max = -Infinity,
        total_max = -Infinity;

    source.forEachFeatureInExtent(extent, function(f) {
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
  };

  /**
   * Setup the event handlers for the 'preremove' and 'add' events.
   */
  function setupEvents() {
    $(collection).on('preremove', function(e, flight) {
      source.removeFeature(
          source.getFeatures().filter(function(e) {
            return e.get('sfid') == flight.getID();
          })[0]
      );
    });

    $(collection).on('add', function(e, flight) {
      var feature = new ol.Feature({
        geometry: flight.getGeometry(),
        sfid: flight.getID(),
        color: flight.getColor(),
        type: 'flight'
      });

      source.addFeature(feature);
    });
  }

  setupEvents();
  return collection;
};
