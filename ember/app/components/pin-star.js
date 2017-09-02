import Ember from 'ember';
import { includes } from 'ember-awesome-macros/array';

export default Ember.Component.extend({
  pinnedFlights: Ember.inject.service(),

  tagName: 'span',
  classNames: ['pin'],
  classNameBindings: ['pinned'],

  pinned: includes('pinnedFlights.pinned', 'flightId'),

  click() {
    this.get('pinnedFlights').toggle(this.get('flightId'));
  },
});
