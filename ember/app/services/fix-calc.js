import Ember from 'ember';

export default Ember.Service.extend({
  flights: [],
  time: null,

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
});
