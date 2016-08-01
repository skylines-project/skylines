import Ember from 'ember';

import addDays from '../utils/add-days';
import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
  account: Ember.inject.service(),
  pinnedFlights: Ember.inject.service(),

  tagName: 'ul',
  classNames: ['nav', 'nav-pills'],

  hasPinned: Ember.computed.notEmpty('pinnedFlights.pinned'),

  prevDate: safeComputed('date', date => addDays(date, -1)),
  nextDate: safeComputed('date', date => addDays(date, 1)),

  init() {
    this._super(...arguments);
    this.set('router', Ember.getOwner(this).lookup('router:main'));
  },

  actions: {
    dateSelected(date) {
      this.get('router').transitionTo('flights.date', date);
    },
  },
});
