import BarogramComponent from './base-barogram';

export default BarogramComponent.extend({
  prefix: null,
  uploadMode: true,
  height: 160,

  init() {
    this._super(...arguments);
    window[`barogram-${this.get('prefix')}`] = this;
  },

  didInsertElement() {
    this._super(...arguments);

    this.get('placeholder').on('plotselecting', (event, range, marker) => {
      this.trigger('baroselecting', range, marker);
    });
  },

  setFlightTimes(takeoff, scoring_start, scoring_end, landing) {
    this.get('flot').setSelection({
      takeoff: takeoff * 1000,
      scoring_start: scoring_start * 1000,
      scoring_end: scoring_end * 1000,
      landing: landing * 1000,
    });
  },

  updateFlightTime(time, field) {
    this.get('flot').updateSelection(time * 1000, field);
  },

  getFlightTimes() {
    return this.get('flot').getSelection();
  },
});
