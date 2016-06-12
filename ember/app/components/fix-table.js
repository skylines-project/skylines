/* global unpinFlight */

import Ember from 'ember';

export default Ember.Component.extend(Ember.Evented, {
  fixCalc: Ember.inject.service(),

  selection: null,

  data: Ember.computed.map('fixCalc.fixes', function(fix, i) {
    let flight = fix.get('flight');
    let id = flight.get('id');
    let color = flight.get('color');
    let competitionId = flight.get('competition_id');
    let removable = (i !== 0);
    return {id, color, competitionId, removable, fix};
  }),

  selectable: Ember.computed.gt('data.length', 1),

  init() {
    this._super(...arguments);

    window.fixTable = this;
  },

  actions: {
    select(id) {
      if (this.get('selectable')) {
        var current = this.get('selection');
        this.set('selection', current === id ? null : id);
      }
    },

    remove(id) {
      this.trigger('remove_flight', id);
      unpinFlight(id);
    },
  },
});
