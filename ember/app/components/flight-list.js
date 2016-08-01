import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'table',
  classNames: ['table', 'table-striped', 'table-condensed', 'table-flights'],

  flights: [],
  showDate: true,
  showAirport: true,
  showClub: true,
  showPilot: true,
  showTimes: true,
});
