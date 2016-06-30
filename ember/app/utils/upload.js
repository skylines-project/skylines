import Ember from 'ember';
import ol from 'openlayers';

import { convertAltitude } from './units';

/**
 * Add a barogram.
 *
 * Note: _time, _enl, and _height MUST have the same number
 *   of elements when decoded.
 *
 * @param {Ember.Component} baro
 * @param {int} sfid SkyLines flight ID.
 * @param {String} _time Google polyencoded string of time values.
 * @param {String} _height Google polyencoded string of height values.
 * @param {String} _enl Google polyencoded string of engine noise levels.
 * @param {String} _elevations_h Google polyencoded string of elevations.
 * @param {int} takeoff_time Time of takeoff.
 * @param {int} scoring_start_time Time of scoring start.
 * @param {int} scoring_end_time Time of scoring end.
 * @param {int} landing_time Time of landing.
 * @return {Object} Barogram.
 */
export function initBaro(baro, sfid, _time, _height, _enl,
                  _elevations_h, takeoff_time, scoring_start_time,
                  scoring_end_time, landing_time) {

  let height = ol.format.Polyline.decodeDeltas(_height, 1, 1);
  let time = ol.format.Polyline.decodeDeltas(_time, 1, 1);
  let enl = ol.format.Polyline.decodeDeltas(_enl, 1, 1);
  let _elev_h = ol.format.Polyline.decodeDeltas(_elevations_h, 1, 1);

  let flot_h = [], flot_enl = [];
  let flot_elev = [], elev_h = [];
  let timeLength = time.length;
  for (let i = 0; i < timeLength; ++i) {
    let timestamp = time[i] * 1000;
    flot_h.push([timestamp, convertAltitude(height[i])]);
    flot_enl.push([timestamp, enl[i]]);

    let e = _elev_h[i];
    if (e < -500)
      e = null;

    elev_h.push(e);
    flot_elev.push([timestamp, e ? convertAltitude(e) : null]);
  }

  let color = '#004bbd';

  let data = { data: flot_h, color };

  let enl_data = { data: flot_enl, color };

  baro.set('active', [data]);
  baro.set('enls', [enl_data]);
  baro.set('elevations', flot_elev);

  baro.setFlightTimes(
      takeoff_time,
      scoring_start_time,
      scoring_end_time,
      landing_time
  );

  baro.draw();

  return baro;
}


/**
* Update the timepicker values.
*
* @param {number} prefix Prefix of uploaded flight.
* @param {number} flight_date Unix timestamp of takeoff date.
* @param {Object} values Values of the current markers.
*/
export function updateTimePicker(prefix, flight_date, values) {
  let takeOffTimePicker = Ember.$(`#${prefix}-takeoff_time-datetimepicker`);
  if (takeOffTimePicker.data('DateTimePicker').getDate().unix() !=
      parseInt(values.takeoff / 1000)) {
    let datetime = flight_date.clone().add(values.takeoff, 'ms');

    takeOffTimePicker.data('DateTimePicker').setValue(datetime);
    Ember.$(`#${prefix}-takeoff_time`).val(datetime.format('YYYY-MM-DD HH:mm:ss'));
  }

  let scoringStartTimePicker = Ember.$(`#${prefix}-scoring_start_time-datetimepicker`);
  if (scoringStartTimePicker.data('DateTimePicker').getDate().unix() !=
      parseInt(values.scoring_start / 1000)) {
    let datetime = flight_date.clone().add(values.scoring_start, 'ms');

    scoringStartTimePicker.data('DateTimePicker').setValue(datetime);
    Ember.$(`#${prefix}-scoring_start_time`).val(datetime.format('YYYY-MM-DD HH:mm:ss'));
  }

  let scoringEndTimePicker = Ember.$(`#${prefix}-scoring_end_time-datetimepicker`);
  if (scoringEndTimePicker.data('DateTimePicker').getDate().unix() !=
      parseInt(values.scoring_end / 1000)) {
    let datetime = flight_date.clone().add(values.scoring_end, 'ms');

    scoringEndTimePicker.data('DateTimePicker').setValue(datetime);
    Ember.$(`#${prefix}-scoring_end_time`).val(datetime.format('YYYY-MM-DD HH:mm:ss'));
  }

  let landingTimePicker = Ember.$(`#${prefix}-landing_time-datetimepicker`);
  if (landingTimePicker.data('DateTimePicker').getDate().unix() !=
      parseInt(values.landing / 1000)) {
    let datetime = flight_date.clone().add(values.landing, 'ms');

    landingTimePicker.data('DateTimePicker').setValue(datetime);
    Ember.$(`#${prefix}-landing_time`).val(datetime.format('YYYY-MM-DD HH:mm:ss'));
  }
}
