import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  pinnedFlights: service(),

  tagName: 'span',
  classNames: ['pin'],
  classNameBindings: ['pinned'],

  pinned: computed('pinnedFlights.pinned.[]', 'flightId', function() {
    return this.pinnedFlights.pinned.includes(this.flightId);
  }),

  click() {
    this.pinnedFlights.toggle(this.flightId);
  },
});
