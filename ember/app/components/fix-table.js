/* global unpinFlight */

import Ember from 'ember';

export default Ember.Component.extend(Ember.Evented, {
  data: [],
  selectable: false,
  selection: null,

  init() {
    this._super(...arguments);

    this.set('data', []);

    window.fixTable = this;
  },

  findRow(id) {
    return this.get('data').findBy('id', id);
  },

  addRow(id, color, competitionId) {
    let data = this.get('data');
    if (data.isAny('id', id)) {
      return;
    }

    let removable = (data.length !== 0);

    this.set('data', data.concat([{id, color, competitionId, removable, fix: {}}]));
  },

  removeRow(id) {
    this.set('data', this.get('data').rejectBy('id', id));

    if (this.get('selection') === id) {
      this.set('selection', null);
    }
  },

  clearAllFixes() {
    this.get('data').forEach(it => {
      Ember.set(it, 'fix', {});
    });
  },

  clearFix(id) {
    this.updateFix(id, {});
  },

  updateFix(id, fix) {
    Ember.set(this.findRow(id), 'fix', fix);
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
