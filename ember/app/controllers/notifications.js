import Controller from '@ember/controller';
import { set } from '@ember/object';
import { alias, equal, filterBy, notEmpty, and } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

import safeComputed from '../computed/safe-computed';

export default Controller.extend({
  ajax: service(),
  notifications: service(),

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

  isFirstPage: equal('page', 1),
  unreadEvents: filterBy('events', 'unread', true),
  hasUnreadOnPage: notEmpty('unreadEvents'),
  hasUnread: and('isFirstPage', 'hasUnreadOnPage'),

  markAsReadTask: task(function*() {
    yield this.ajax.request('/api/notifications/clear', { method: 'POST' });
    this.get('model.events').forEach(event => set(event, 'unread', false));
    this.set('notifications.counter', 0);
  }).drop(),
});
