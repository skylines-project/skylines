


/**
 * A contest of a flight.
 * @constructor
 * @param {Array(Objects)} _contest Scored/Optimised contests.
 *   Such an object must contain: name, turnpoints, times
 *   turnpoints and times are googlePolyEncoded strings.
 * @param {Integer} _sfid The SkyLines flight id this contest trace belongs to.
 */
slContest = function(_contest, _sfid) {
  var contest = {};

  var sfid = _sfid;
  var geometry;
  var color;
  var times;
  var name;

  var contest_colors = {
    'olc_plus classic': '#ff2c73',
    'olc_plus triangle': '#9f14ff'
  };

  contest.init = function(_contest) {
    var turnpoints = ol.format.Polyline.decodeDeltas(_contest.turnpoints, 2);
    times = ol.format.Polyline.decodeDeltas(_contest.times, 1, 1);
    name = _contest.name;

    geometry = new ol.geom.LineString([]);
    var turnpointsLength = turnpoints.length;

    var triangle = (name.search(/triangle/) != -1 && turnpointsLength == 5 * 2);

    if (triangle) turnpointsLength -= 2;

    for (var i = 0; i < turnpointsLength; i += 2) {
      var point = ol.proj.transform([turnpoints[i + 1], turnpoints[i]],
                                    'EPSG:4326', 'EPSG:3857');
      geometry.appendCoordinate(point);
    }

    if (triangle) {
      geometry.appendCoordinate(geometry.getFirstCoordinate());
    }

    color = contest_colors[name] || '#ff2c73';
  };

  contest.getGeometry = function() {
    return geometry;
  };

  contest.getID = function() {
    return sfid;
  };

  contest.getColor = function() {
    return color;
  };

  contest.getTimes = function() {
    return times;
  };

  contest.init(_contest);
  return contest;
};
