/**
 * An ordered collection of flight objects.
 * @constructor
 */
var slFlightCollection = Backbone.Collection.extend({
  // Public attributes and methods
  source: new ol.source.Vector(),

  // Default URL root
  urlRoot: '/flights/',

  initialize: function() {
    this.listenTo(this, 'add', this.addToSource);
    this.listenTo(this, 'remove', this.removeFromSource);
    this.listenTo(this, 'remove', function() {
      if (this.length == 1)
        this.select(this.at(0));
    });
  },

  /**
   * Calculates the bounds of all flights in the collection.
   * @return {ol.extent}
   */
  getBounds: function() {
    return this.source.getExtent();
  },

  /**
   * Returns the vector layer source of this collection.
   * @return {ol.source.Vector}
   */
  getSource: function() {
    return this.source;
  },

  /**
   * Returns the minimum and maximum fix time within the extent.
   * Code based on ol.render.canvas.Replay.prototype.appendFlatCoordinates.
   * @param {ol.extent} extent
   * @return {Object}
   */
  getMinMaxTimeInExtent: function(extent) {
    var min = Infinity,
        total_min = Infinity;
    var max = -Infinity,
        total_max = -Infinity;

    this.source.forEachFeatureInExtent(extent, function(f) {
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

  has: function(sfid) {
    return this.get(sfid);
  },

  /**
   * Some event listeners for the 'remove' and 'add' events.
   */
  removeFromSource: function(flight) {
    this.source.removeFeature(
        this.source.getFeatures().filter(function(e) {
          return e.get('sfid') == flight.getID();
        })[0]
    );
  },

  addToSource: function(flight) {
    var feature = new ol.Feature({
      geometry: flight.getGeometry(),
      sfid: flight.getID(),
      color: flight.getColor(),
      type: 'flight'
    });

    this.source.addFeature(feature);
  },

  select: function(selected_flight) {
    if (this.length == 1) {
      selected_flight.setSelection(true);
      this.trigger('change:selection', selected_flight);
      return;
    }

    if (selected_flight.getSelection())
      selected_flight.setSelection(false);
    else
      selected_flight.setSelection(true);

    this.each(function(flight) {
      if (flight != selected_flight)
        flight.setSelection(false);
    });

    this.trigger('change:selection', selected_flight);
  }
});
