import Controller from '@ember/controller';
import { set } from '@ember/object';
import { and, notEmpty, filterBy, equal, alias } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

import safeComputed from '../computed/safe-computed';

export default class NotificationsController extends Controller {
  @service ajax;
  @service notificationCounter;

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

  @equal('page', 1) isFirstPage;
  @filterBy('events', 'unread', true) unreadEvents;
  @notEmpty('unreadEvents') hasUnreadOnPage;
  @and('isFirstPage', 'hasUnreadOnPage') hasUnread;

  @(task(function* () {
    yield this.ajax.request('/api/notifications/clear', { method: 'POST' });
    this.get('model.events').forEach(event => set(event, 'unread', false));
    this.set('notificationCounter.counter', 0);
  }).drop())
  markAsReadTask;
}
