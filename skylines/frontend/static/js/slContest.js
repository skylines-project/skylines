/**
 * A contest of a flight.
 * @constructor
 * @param {Array<Object>} _contest Scored/Optimised contests.
 *   Such an object must contain: name, turnpoints, times
 *   turnpoints and times are googlePolyEncoded strings.
 * @param {Number} _sfid The SkyLines flight id this contest trace belongs to.
 */
slContest = function(_contest, _sfid) {
  var contest = {};

  /**
   * SkyLines flight ID this contest belongs to.
   * @type {Number}
   */
  var sfid = _sfid;

  /**
   * Geometry of the contest trace.
   * @type {ol.geom.LineString}
   */
  var geometry;

  /**
   * Drawing color.
   * @type {String}
   */
  var color;

  /**
   * Time of each turnpoint
   * @type {Array<Number>}
   */
  var times;

  /**
   * Internal contest type name
   * @type {String}
   */
  var name;


  /**
   * Dictionary of contest names and their colors.
   */
  var contest_colors = {
    'olc_plus classic': '#ff2c73',
    'olc_plus triangle': '#9f14ff'
  };

  /**
   * Decodes the input data and stores it.
   * @param {Object} _contest Contest object
   */
  contest.init = function(_contest) {
    var turnpoints = ol.format.Polyline.decodeDeltas(_contest.turnpoints, 2);
    times = ol.format.Polyline.decodeDeltas(_contest.times, 1, 1);
    name = _contest.name;

    geometry = new ol.geom.LineString([]);
    var turnpointsLength = turnpoints.length;
    var triangle = (name.search(/triangle/) != -1 && turnpointsLength == 5 * 2);

    if (triangle) {
      for (var i = 2; i < turnpointsLength - 2; i += 2) {
        var point = ol.proj.transform([turnpoints[i + 1], turnpoints[i]],
                                      'EPSG:4326', 'EPSG:3857');
        geometry.appendCoordinate(point);
      }

      geometry.appendCoordinate(geometry.getFirstCoordinate());
    } else {
      for (var i = 0; i < turnpointsLength; i += 2) {
        var point = ol.proj.transform([turnpoints[i + 1], turnpoints[i]],
                                      'EPSG:4326', 'EPSG:3857');
        geometry.appendCoordinate(point);
      }
    }

    color = contest_colors[name] || '#ff2c73';
  };

  /**
   * Returns the geometry of the contest trace
   * @return {ol.geom.LineString}
   */
  contest.getGeometry = function() {
    return geometry;
  };

  /**
   * Returns the SkyLines id of the contest's flight
   * @return {Number}
   */
  contest.getID = function() {
    return sfid;
  };

  /**
   * Returns the contest drawing color
   * @return {String}
   */
  contest.getColor = function() {
    return color;
  };

  /**
   * Returns the turnpoint time array
   * @return {Array<Number>}
   */
  contest.getTimes = function() {
    return times;
  };

  contest.init(_contest);
  return contest;
};
