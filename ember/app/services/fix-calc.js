import Ember from 'ember';

export default Ember.Service.extend({
  flights: [],
  time: null,
  timer: null,

  isRunning: Ember.computed.bool('timer'),

  startTimes: Ember.computed.mapBy('flights', 'time.firstObject'),
  minStartTime: Ember.computed.min('startTimes'),

  endTimes: Ember.computed.mapBy('flights', 'time.lastObject'),
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
