import Ember from 'ember';
import { includes } from 'ember-awesome-macros';

export default Ember.Component.extend({
  pinnedFlights: Ember.inject.service(),

  classNames: 'btn btn-default',

  pinned: includes('pinnedFlights.pinned', 'flightId'),

  click() {
    this.get('pinnedFlights').toggle(this.get('flightId'));
  },
});
