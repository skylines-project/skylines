import { getOwner } from '@ember/application';
import { notEmpty } from '@ember/object/computed';
import { inject as service } from '@ember/service';
import Component from '@ember/component';

import addDays from '../utils/add-days';
import safeComputed from '../computed/safe-computed';

export default Component.extend({
  account: service(),
  pinnedFlights: service(),

  tagName: '',

  hasPinned: notEmpty('pinnedFlights.pinned'),

  prevDate: safeComputed('date', date => addDays(date, -1)),
  nextDate: safeComputed('date', date => addDays(date, 1)),

  init() {
    this._super(...arguments);
    this.set('router', getOwner(this).lookup('router:main'));
  },

  actions: {
    dateSelected(date) {
      this.get('router').transitionTo('flights.date', date);
    },
  },
});
