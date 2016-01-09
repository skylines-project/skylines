/**
 * Represents a waypoint.
 * @constructor
 */
var slWaypoint = Backbone.Model.extend({
  idAttribute: 'waypoint_id',

  defaults: function() {
    return {
      /**
       * Unique waypoint ID. Shall be used to identify waypoint
       * in SkyLines database. 'null' means this waypoint is not
       * stored in the database (e.g. free waypoints).
       * @type {Number}
       * @private
       */
      waypoint_id: null,

      /**
       * Location of this waypoint.
       * @type {ol.Coordinate}
       * @private
       */
      coordinate: null,

      name: null,
      type: null
    };
  },

  /**
   * Returns the coordinate of this waypoint.
   * @return {ol.Coordinate}
   */
  getCoordinate: function() {
    return this.attributes.coordinate;
  },

  getName: function() {
    return this.attributes.name;
  }
});
