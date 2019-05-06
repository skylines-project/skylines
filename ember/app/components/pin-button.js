import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { includes } from 'ember-awesome-macros/array';

export default Component.extend({
  pinnedFlights: service(),

  tagName: '',

  pinned: includes('pinnedFlights.pinned', 'flightId'),

  actions: {
    toggle() {
      this.pinnedFlights.toggle(this.flightId);
    },
  },
});
