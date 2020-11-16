import { decodeDeltas } from 'ol/format/Polyline';

import Contest from './contest';
import Flight from './flight';

export default function (data, units) {
  let _time = decodeDeltas(data.barogram_t, 1, 1);
  let _lonlat = decodeDeltas(data.points, 2);
  let _height = decodeDeltas(data.barogram_h, 1, 1);
  let _enl = decodeDeltas(data.enl, 1, 1);

  let fixes = _time.map(function (timestamp, i) {
    return {
      time: timestamp,
      longitude: _lonlat[i * 2],
      latitude: _lonlat[i * 2 + 1],
      altitude: _height[i] + data.geoid,
      enl: _enl[i],
    };
  });

  let _elev_t = decodeDeltas(data.elevations_t, 1, 1);
  let _elev_h = decodeDeltas(data.elevations_h, 1, 1);

  let elevations = _elev_t.map(function (timestamp, i) {
    let elevation = _elev_h[i];

    return {
      time: timestamp,
      elevation: elevation > -500 ? elevation : null,
    };
  });

  let additional = data.additional || {};

  let contests;
  if (data.contests) {
    contests = data.contests.map(it => new Contest(it));
  }

  return Flight.create({
    units,
    id: data.sfid,
    fixes,
    elevations,
    contests,
    geoid: data.geoid,
    competition_id: additional.competition_id,
    registration: additional.registration,
    model: additional.model,
  });
}
