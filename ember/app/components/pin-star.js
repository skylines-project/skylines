import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { includes } from 'ember-awesome-macros/array';

export default Component.extend({
  pinnedFlights: service(),

  tagName: 'span',
  classNames: ['pin'],
  classNameBindings: ['pinned'],

  pinned: includes('pinnedFlights.pinned', 'flightId'),

  click() {
    this.get('pinnedFlights').toggle(this.get('flightId'));
  },
});
