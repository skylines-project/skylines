import Ember from 'ember';

export default Ember.Component.extend({
  pinnedFlights: Ember.inject.service(),

  tagName: 'span',
  classNames: ['pin'],
  classNameBindings: ['pinned'],

  pinned: Ember.computed('flightId', 'pinnedFlights.pinned.[]', function() {
    return this.get('pinnedFlights.pinned').includes(this.get('flightId'));
  }),

  didInsertElement() {
    this.$().tooltip({
      placement: 'left',
      title: 'Activate this to show the flight on top of other flights on the map',
    });
  },

  click() {
    this.get('pinnedFlights').toggle(this.get('flightId'));
  },
});
