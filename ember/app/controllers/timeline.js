import Controller from '@ember/controller';
import { alias } from '@ember/object/computed';

import safeComputed from '../computed/safe-computed';

export default Controller.extend({
  queryParams: ['page', 'user', 'type'],
  page: 1,
  user: null,
  type: null,

  events: alias('model.events'),

  prevPage: safeComputed('page', page => {
    if (page > 1) {
      return page - 1;
    }
  }),

  nextPage: safeComputed('page', 'events.length', 'perPage', (page, numEvents, perPage) => {
    if (numEvents === perPage) {
      return page + 1;
    }
  }),
});
