/**
 * Add a barogram.
 *
 * Note: _time, _enl, and _height MUST have the same number
 *   of elements when decoded.
 *
 * @param {DOMElement} placeholder DOM element for the barogram.
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
function initBaro(placeholder, sfid, _time, _height, _enl,
                  _elevations_h, takeoff_time, scoring_start_time,
                  scoring_end_time, landing_time) {
  var height = ol.format.Polyline.decodeDeltas(_height, 1, 1);
  var time = ol.format.Polyline.decodeDeltas(_time, 1, 1);
  var enl = ol.format.Polyline.decodeDeltas(_enl, 1, 1);
  var _elev_h = ol.format.Polyline.decodeDeltas(_elevations_h, 1, 1);

  var flot_h = [], flot_enl = [];
  var flot_elev = [], elev_h = [];
  var timeLength = time.length;
  for (var i = 0; i < timeLength; ++i) {
    var timestamp = time[i] * 1000;
    flot_h.push([timestamp, slUnits.convertAltitude(height[i])]);
    flot_enl.push([timestamp, enl[i]]);

    var e = _elev_h[i];
    if (e < -500)
      e = null;

    elev_h.push(e);
    flot_elev.push([timestamp, e ? slUnits.convertAltitude(e) : null]);
  }

  var color = '#004bbd';

  var data = {
    data: flot_h,
    color: color
  };

  var enl_data = {
    data: flot_enl,
    color: color
  };

  var baro_opts = {
    selection: {
      mode: 'x'
    },
    crosshair: {
      mode: null
    }
  };

  var baro = slBarogram(placeholder, baro_opts);
  baro.setActiveTraces([data]);
  baro.setENLData([enl_data]);
  baro.setElevations(flot_elev);

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
function updateTimePicker(prefix, flight_date, values) {
  var takeOffTimePicker = $('#' + prefix + '-takeoff_time-datetimepicker');
  if (takeOffTimePicker.data('DateTimePicker').getDate().unix() !=
      parseInt(values.takeoff / 1000)) {
    var datetime = flight_date.clone().add('ms', values.takeoff);

    takeOffTimePicker.data('DateTimePicker').setValue(datetime);
    $('#' + prefix + '-takeoff_time')
        .val(datetime.format('YYYY-MM-DD HH:mm:ss'));
  }

  var scoringStartTimePicket =
      $('#' + prefix + '-scoring_start_time-datetimepicker');
  if (scoringStartTimePicket.data('DateTimePicker').getDate().unix() !=
      parseInt(values.scoring_start / 1000)) {
    var datetime = flight_date.clone().add('ms', values.scoring_start);

    scoringStartTimePicket.data('DateTimePicker').setValue(datetime);
    $('#' + prefix + '-scoring_start_time')
        .val(datetime.format('YYYY-MM-DD HH:mm:ss'));
  }

  var scoringEndTimePicker =
      $('#' + prefix + '-scoring_end_time-datetimepicker');
  if (scoringEndTimePicker.data('DateTimePicker').getDate().unix() !=
      parseInt(values.scoring_end / 1000)) {
    var datetime = flight_date.clone().add('ms', values.scoring_end);

    scoringEndTimePicker.data('DateTimePicker').setValue(datetime);
    $('#' + prefix + '-scoring_end_time')
        .val(datetime.format('YYYY-MM-DD HH:mm:ss'));
  }

  var landingTimePicker = $('#' + prefix + '-landing_time-datetimepicker');
  if (landingTimePicker.data('DateTimePicker').getDate().unix() !=
      parseInt(values.landing / 1000)) {
    var datetime = flight_date.clone().add('ms', values.landing);

    landingTimePicker.data('DateTimePicker').setValue(datetime);
    $('#' + prefix + '-landing_time')
        .val(datetime.format('YYYY-MM-DD HH:mm:ss'));
  }
}
