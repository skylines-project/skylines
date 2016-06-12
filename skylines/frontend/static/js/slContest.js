/**
 * A contest of a flight.
 * @constructor
 * @param {Array<Object>} _contest Scored/Optimised contests.
 *   Such an object must contain: name, turnpoints, times
 *   turnpoints and times are googlePolyEncoded strings.
 * @param {Number} _sfid The SkyLines flight id this contest trace belongs to.
 */
var slContest = Backbone.Model.extend({
  // Default attributes for the contest
  defaults: function() {
    return {
      /**
       * SkyLines flight ID this contest belongs to.
       * @type {Number}
       */
      sfid: null,

      /**
       * Geometry of the contest trace.
       * @type {ol.geom.LineString}
       */
      geometry: new ol.geom.LineString([]),

      /**
       * Drawing color.
       * @type {String}
       */
      color: null,

      /**
       * Time of each turnpoint
       * @type {Array<Number>}
       */
      times: null,

      /**
       * Internal contest type name
       * @type {String}
       */
      name: null
    };
  },


  /**
   * Dictionary of contest names and their colors.
   */
  contest_colors: {
    'olc_plus classic': '#ff2c73',
    'olc_plus triangle': '#9f14ff'
  },

  /**
   * Decodes the input data and stores it.
   * @param {Object} _contest Contest object
   */
  parse: function(_contest) {
    var attrs = this.defaults();

    var turnpoints = ol.format.Polyline.decodeDeltas(_contest.turnpoints, 2);
    attrs.times = ol.format.Polyline.decodeDeltas(_contest.times, 1, 1);
    attrs.name = _contest.name;

    var turnpointsLength = turnpoints.length;
    var triangle = (attrs.name.search(/triangle/) != -1 &&
                    turnpointsLength == 5 * 2);

    if (triangle) {
      for (var i = 2; i < turnpointsLength - 2; i += 2) {
        var point = ol.proj.transform([turnpoints[i + 1], turnpoints[i]],
                                      'EPSG:4326', 'EPSG:3857');
        attrs.geometry.appendCoordinate(point);
      }

      attrs.geometry.appendCoordinate(attrs.geometry.getFirstCoordinate());
    } else {
      for (var i = 0; i < turnpointsLength; i += 2) {
        var point = ol.proj.transform([turnpoints[i + 1], turnpoints[i]],
                                      'EPSG:4326', 'EPSG:3857');
        attrs.geometry.appendCoordinate(point);
      }
    }

    attrs.color = this.contest_colors[attrs.name] || '#ff2c73';
    attrs.sfid = _contest.sfid;
    return attrs;
  },

  /**
   * Returns the geometry of the contest trace
   * @return {ol.geom.LineString}
   */
  getGeometry: function() {
    return this.attributes.geometry;
  },

  /**
   * Returns the SkyLines id of the contest's flight
   * @return {Number}
   */
  getID: function() {
    return this.attributes.sfid;
  },

  /**
   * Returns the contest drawing color
   * @return {String}
   */
  getColor: function() {
    return this.attributes.color;
  },

  /**
   * Returns the turnpoint time array
   * @return {Array<Number>}
   */
  getTimes: function() {
    return this.attributes.times;
  }
});
