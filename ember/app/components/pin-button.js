import Ember from 'ember';
import { includes } from 'ember-awesome-macros';

export default Ember.Component.extend({
  pinnedFlights: Ember.inject.service(),

  tagName: '',

  pinned: includes('pinnedFlights.pinned', 'flightId'),

  actions: {
    toggle() {
      this.get('pinnedFlights').toggle(this.get('flightId'));
    },
  },
});
