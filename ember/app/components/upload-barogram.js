import { action, computed } from '@ember/object';
import { readOnly } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import ol from 'openlayers';

import BarogramComponent from './base-barogram';

export default BarogramComponent.extend({
  units: service(),

  uploadMode: true,
  height: 160,

  flight: null,
  trace: null,

  date: readOnly('flight.igcFile.date'),

  takeoffTime: null,
  scoreStartTime: null,
  scoreEndTime: null,
  landingTime: null,

  takeoffTimeSeconds: computedSecondsOfDay('date', 'takeoffTime'),
  scoreStartTimeSeconds: computedSecondsOfDay('date', 'scoreStartTime'),
  scoreEndTimeSeconds: computedSecondsOfDay('date', 'scoreEndTime'),
  landingTimeSeconds: computedSecondsOfDay('date', 'landingTime'),

  onTakeoffTimeChange() {},
  onScoreStartTimeChange() {},
  onScoreEndTimeChange() {},
  onLandingTimeChange() {},

  init() {
    this._super(...arguments);
    let units = this.units;

    let height = ol.format.Polyline.decodeDeltas(this.get('trace.barogram_h'), 1, 1);
    let time = ol.format.Polyline.decodeDeltas(this.get('trace.barogram_t'), 1, 1);
    let enl = ol.format.Polyline.decodeDeltas(this.get('trace.enl'), 1, 1);
    let _elev_h = ol.format.Polyline.decodeDeltas(this.get('trace.elevations_h'), 1, 1);

    let flot_h = [];
    let flot_enl = [];
    let flot_elev = [];
    let timeLength = time.length;
    for (let i = 0; i < timeLength; ++i) {
      let timestamp = time[i] * 1000;
      flot_h.push([timestamp, units.convertAltitude(height[i])]);
      flot_enl.push([timestamp, enl[i]]);

      let e = _elev_h[i];
      if (e < -500) {
        e = null;
      }

      flot_elev.push([timestamp, e ? units.convertAltitude(e) : null]);
    }

    let color = '#004bbd';

    this.set('active', [{ data: flot_h, color }]);
    this.set('enls', [{ data: flot_enl, color }]);
    this.set('elevations', flot_elev);
  },

  initFlot: action(function(element) {
    this._initFlot(element);

    this.placeholder.on('plotselecting', (event, range, marker) => {
      let date = secondsToDate(this.date, range[marker]);

      if (marker === 'takeoff') {
        this.onTakeoffTimeChange(date);
      } else if (marker === 'scoring_start') {
        this.onScoreStartTimeChange(date);
      } else if (marker === 'scoring_end') {
        this.onScoreEndTimeChange(date);
      } else if (marker === 'landing') {
        this.onLandingTimeChange(date);
      }
    });

    this.updateSelection();
    this.draw();
  }),

  didUpdateAttrs() {
    this._super(...arguments);
    this.updateSelection();
  },

  updateSelection() {
    let takeoff = this.takeoffTimeSeconds;
    let scoring_start = this.scoreStartTimeSeconds;
    let scoring_end = this.scoreEndTimeSeconds;
    let landing = this.landingTimeSeconds;

    this.flot.setSelection({ takeoff, scoring_start, scoring_end, landing }, true);
  },
});

function computedSecondsOfDay(dateKey, timeKey) {
  return computed(dateKey, timeKey, function() {
    let date = new Date(this.get(dateKey));
    date.setUTCHours(0, 0, 0, 0);

    let time = new Date(this.get(timeKey));

    return time.getTime() - date.getTime();
  });
}

function secondsToDate(date, seconds) {
  date = new Date(date);
  date.setUTCHours(0, 0, 0, 0);

  return new Date(date.getTime() + seconds);
}
