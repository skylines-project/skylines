import Ember from 'ember';

export default Ember.Component.extend({
  pinnedFlights: Ember.inject.service(),

  classNames: 'btn btn-default',

  pinned: Ember.computed('flightId', 'pinnedFlights.pinned.[]', function() {
    return this.get('pinnedFlights.pinned').contains(this.get('flightId'));
  }),

  click() {
    this.get('pinnedFlights').toggle(this.get('flightId'));
  }
});
