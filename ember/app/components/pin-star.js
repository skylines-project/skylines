import Ember from 'ember';
import { includes } from 'ember-awesome-macros';

export default Ember.Component.extend({
  pinnedFlights: Ember.inject.service(),

  tagName: 'span',
  classNames: ['pin'],
  classNameBindings: ['pinned'],

  pinned: includes('pinnedFlights.pinned', 'flightId'),

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
