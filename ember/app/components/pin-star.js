import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default Component.extend({
  pinnedFlights: service(),
  tagName: '',

  pinned: computed('pinnedFlights.pinned.[]', 'flightId', function() {
    return this.pinnedFlights.pinned.includes(this.flightId);
  }),

  handleClick: action(function() {
    this.pinnedFlights.toggle(this.flightId);
  }),
});
