/**
 * Add a barogram.
 *
 * Note: _time, _enl, and _height MUST have the same number
 *   of elements when decoded.
 *
 * @param {DOMElement} placeholder DOM element for the barogram.
 * @param {Object} data Flight data.
 * @param {int} takeoff_time Time of takeoff.
 * @param {int} scoring_start_time Time of scoring start.
 * @param {int} scoring_end_time Time of scoring end.
 * @param {int} landing_time Time of landing.
 * @return {Object} Barogram.
 */
function initBaro(placeholder, data,
                  takeoff_time, scoring_start_time,
                  scoring_end_time, landing_time) {
  var flight = new slFlight(data, {parse: true});
  flight.setColor('#004bbd');

  var baro_opts = {
    selection: {
      mode: 'x'
    },
    crosshair: {
      mode: null
    }
  };

  var collection = new Backbone.Collection();
  collection.add(flight);

  var baro = new slBarogramView({
    el: placeholder,
    collection: collection,
    attributes: baro_opts
  });

  baro.setFlightTimes(
      takeoff_time,
      scoring_start_time,
      scoring_end_time,
      landing_time
  );

  baro.render();

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
