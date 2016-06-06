/**
 * Dictionary of contest names and their colors.
 */
var contest_colors = {
  'olc_plus classic': '#ff2c73',
  'olc_plus triangle': '#9f14ff'
};

/**
 * A contest of a flight.
 * @constructor
 * @param {Array<Object>} _contest Scored/Optimised contests.
 *   Such an object must contain: name, turnpoints, times
 *   turnpoints and times are googlePolyEncoded strings.
 * @param {Number} _sfid The SkyLines flight id this contest trace belongs to.
 */
slContest = Ember.Object.extend();

slContest.fromData = function(_contest, flightId) {
  var turnpoints = ol.format.Polyline.decodeDeltas(_contest.turnpoints, 2);
  var times = ol.format.Polyline.decodeDeltas(_contest.times, 1, 1);
  var name = _contest.name;

  var geometry = new ol.geom.LineString([]);
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

  var color = contest_colors[name] || '#ff2c73';

  return slContest.create({
    flightId: flightId,
    times: times,
    name: name,
    geometry: geometry,
    color: color
  })
};