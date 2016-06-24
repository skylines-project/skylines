import Ember from 'ember';

import safeComputed from '../utils/safe-computed';

export default Ember.Controller.extend({
  queryParams: ['page', 'user', 'type'],
  page: 1,
  user: null,
  type: null,

  events: Ember.computed.alias('model.events'),

  prevPage: safeComputed('page', page => {
    if (page > 1) {
      return page - 1;
    }
  }),

  nextPage: safeComputed('page', 'events.length', 'perPage', (page, numEvents, perPage) => {
    if (numEvents == perPage) {
      return page + 1;
    }
  }),
});
