import Ember from 'ember';

export default Ember.Service.extend({
  flights: [],

  /*
   * Global time, can be:
   * null -> no time is set, don't show barogram crosshair/plane position
   * -1 -> always show the latest time/fix for each flight
   * >= 0 -> show the associated time in the barogram and on the map
   * @type {!Number}
   */
  time: null,

  timer: null,

  isRunning: Ember.computed.bool('timer'),

  startTimes: Ember.computed.mapBy('flights', 'startTime'),
  minStartTime: Ember.computed.min('startTimes'),

  endTimes: Ember.computed.mapBy('flights', 'endTime'),
  maxEndTime: Ember.computed.max('endTimes'),

  data: Ember.computed('flights.@each.time', 'time', function() {
    let time = this.get('time');
    return this.get('flights').map(flight => [flight, flight.getFixData(time)]);
  }),

  init() {
    this._super(...arguments);
    window.fixCalcService = this;
  },

  startPlayback() {
    let time = this.get('time');

    if (time === null || time === -1) {
      this.set('time', this.get('minStartTime'));
    }

    this.set('timer', Ember.run.later(this, 'onTick', 50));
  },

  stopPlayback() {
    let timer = this.get('timer');
    if (timer) {
      Ember.run.cancel(timer);
      this.set('timer', null);
    }
  },

  onTick() {
    let time = this.get('time') + 1;

    if (time > this.get('maxEndTime')) {
      this.stopPlayback();
    }

    this.set('time', time);
    this.set('timer', Ember.run.later(this, 'onTick', 50));
  }
});
