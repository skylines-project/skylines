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

  initialize: function() {
    this.attributes.sector =
        new slTurnpointSector(this.attributes.coordinate, 0, 'daec');
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
   * Modify turnpoint type.
   */
  changeTurnpointType: function() {
    this.trigger('change:type', this);
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
   * Updates the legs to the previous and next turnpoint.
   */
  setBearings: function(prev_bearing, next_bearing) {
    this.attributes.previous_bearing = prev_bearing;
    this.attributes.next_bearing = next_bearing;

    if (prev_bearing == null)
      this.attributes.sector.updateGeometry(
          this.getCoordinate(), next_bearing - 180
      );
    else if (next_bearing == null)
      this.attributes.sector.updateGeometry(
          this.getCoordinate(), prev_bearing - 180
      );
    else {
      var a = next_bearing / 180 * Math.PI;
      var b = prev_bearing / 180 * Math.PI;

      var angle = Math.atan2((Math.sin(a) + Math.sin(b)) / 2,
                             (Math.cos(a) + Math.cos(b)) / 2);

      angle = angle * 180 / Math.PI + 180;

      this.attributes.sector.updateGeometry(this.getCoordinate(), angle);
    }
  },

  getGeometry: function() {
    return this.attributes.sector.getGeometry();
  },

  getID: function() {
    return this.id;
  },

  getWaypoint: function() {
    return this.attributes.waypoint;
  }
});
