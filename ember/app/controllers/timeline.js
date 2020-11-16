import Controller from '@ember/controller';
import { alias } from '@ember/object/computed';

import safeComputed from '../computed/safe-computed';

export default class TimelineController extends Controller {
  queryParams = ['page', 'user', 'type'];
  page = 1;
  user = null;
  type = null;

  @alias('model.events') events;

  @safeComputed('page', page => {
    if (page > 1) {
      return page - 1;
    }
  })
  prevPage;

  @safeComputed('page', 'events.length', 'perPage', (page, numEvents, perPage) => {
    if (numEvents === perPage) {
      return page + 1;
    }
  })
  nextPage;
}
