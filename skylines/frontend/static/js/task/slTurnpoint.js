/**
 * Represents a turnpoint.
 * @constructor
 */
var slTurnpoint = Backbone.Model.extend({
  defaults: function() {
    return {
      /**
       * Sector type.
       * @type {slTurnpointSector}
       */
      sector: null,

      /**
       * Reference waypoint. Should be read-only.
       * @type {slWaypoint}
       */
      waypoint: null,

      /**
       * Coordinate of this turnpoint.
       * @type {ol.Coordinate}
       */
      coordinate: null,

      /**
       * Direction to previous turnpoint (null if none)
       * @type {Number}
       */
      previous_bearing: null,

      /**
       * Direction to next turnpoint (null if none)
       * @type {Number}
       */
      next_bearing: null
    };
  },

  /**
   * Returns the coordinate of this turnpoint.
   * @return {ol.Coordinate}
   */
  getCoordinate: function() {
    if (this.attributes.waypoint != null)
      return this.attributes.waypoint.getCoordinate();
    else
      return this.attributes.coordinate;
  },

  /**
   * Sets the coordinate of this turnpoint.
   */
  setCoordinate: function(coord) {
    // unset waypoint
    this.attributes.waypoint = null;
    this.attributes.coordinate = coord;
    this.trigger('change:coordinate', this);
  },

  /**
   * Clamp turnpoint to waypoint.
   */
  setWaypoint: function(wp) {
    this.attributes.waypoint = wp;
    this.attributes.coordinate = wp.getCoordinate();
    this.trigger('change:coordinate', this);
  },

  /**
   * Updates the leg to the previous turnpoint.
   */
  updatePrevious: function(tp) {
    if (tp == null) {
      this.attributes.previous_bearing = null;
    } else {
      var previous_coord = tp.getCoordinate();
    }
  }
});
