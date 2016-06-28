import Ember from 'ember';

export default Ember.Component.extend({
  tagName: 'tr',
  classNameBindings: ['private:not_published'],

  flight: null,

  pilotName: Ember.computed.or('flight.pilot.name', 'flight.pilotName'),
  copilotName: Ember.computed.or('flight.copilot.name', 'flight.copilotName'),
});
