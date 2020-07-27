import EmberObject from '@ember/object';

import { decodeDeltas } from 'ol/format/Polyline';
import LineString from 'ol/geom/LineString';
import { fromLonLat } from 'ol/proj';

/**
 * Dictionary of contest names and their colors.
 */
const CONTEST_COLORS = {
  'olc_plus classic': '#ff2c73',
  'olc_plus triangle': '#9f14ff',
};

/**
 * A contest of a flight.
 * @constructor
 * @param {Array<Object>} _contest Scored/Optimised contests.
 *   Such an object must contain: name, turnpoints, times
 *   turnpoints and times are googlePolyEncoded strings.
 * @param {Number} _sfid The SkyLines flight id this contest trace belongs to.
 */
export default class slContest extends EmberObject {
  static fromData(_contest, flightId) {
    let turnpoints = decodeDeltas(_contest.turnpoints, 2);
    let times = decodeDeltas(_contest.times, 1, 1);
    let name = _contest.name;

    let geometry = new LineString([]);
    let turnpointsLength = turnpoints.length;
    let triangle = name.search(/triangle/) !== -1 && turnpointsLength === 5 * 2;

    if (triangle) {
      for (let i = 2; i < turnpointsLength - 2; i += 2) {
        let point = fromLonLat([turnpoints[i + 1], turnpoints[i]]);
        geometry.appendCoordinate(point);
      }

      geometry.appendCoordinate(geometry.getFirstCoordinate());
    } else {
      for (let i = 0; i < turnpointsLength; i += 2) {
        let point = fromLonLat([turnpoints[i + 1], turnpoints[i]]);
        geometry.appendCoordinate(point);
      }
    }

    let color = CONTEST_COLORS[name] || '#ff2c73';

    return slContest.create({
      flightId,
      times,
      name,
      geometry,
      color,
    });
  }
}
