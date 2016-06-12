/**
 * An ordered collection of contest objects.
 * @constructor
 */
var slContestCollection = Backbone.Collection.extend({
  // Public attributes and methods
  source: new ol.source.Vector(),

  initialize: function() {
    this.listenTo(this, 'add', this.addToSource);
    this.listenTo(this, 'remove', this.removeFromSource);
  },

  /**
   * Returns the vector layer source of this collection.
   * @return {ol.source.Vector}
   */
  getSource: function() {
    return this.source;
  },

  /**
   * Setup event handlers for the 'add' and 'remove' events
   */
  removeFromSource: function(contest) {
    var features = this.source.getFeatures().filter(function(e) {
      return e.get('sfid') == contest.getID();
    });

    for (var i = 0; i < features.length; ++i) {
      this.source.removeFeature(features[i]);
    }
  },

  addToSource: function(contest) {
    var feature = new ol.Feature({
      geometry: contest.getGeometry(),
      sfid: contest.getID(),
      color: contest.getColor(),
      type: 'contest'
    });

    this.source.addFeature(feature);
  }
});
