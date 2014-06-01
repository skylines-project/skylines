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
 */
function initBaro(placeholder, sfid, _time, _height, _enl,
                  _elevations_h) {
  var polyline_decoder = new OpenLayers.Format.EncodedPolyline();

  var height = polyline_decoder.decodeDeltas(_height, 1, 1);
  var time = polyline_decoder.decodeDeltas(_time, 1, 1);
  var enl = polyline_decoder.decodeDeltas(_enl, 1, 1);
  var _elev_h = polyline_decoder.decodeDeltas(_elevations_h, 1, 1);

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

  baro = slBarogram(placeholder);
  baro.setActiveTraces([data]);
  baro.setENLData([enl_data]);
  baro.setElevations(flot_elev);

  baro.draw();
}
