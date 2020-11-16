import { computed } from '@ember/object';
import { gt } from '@ember/object/computed';
import Service, { inject as service } from '@ember/service';

import { task, rawTimeout } from 'ember-concurrency';

export default class NotificationCounterService extends Service {
  @service ajax;

  counter = 0;
  @gt('counter', 0) hasUnread;

  @computed('counter')
  get counterText() {
    let counter = this.counter;
    return counter > 10 ? '10+' : counter;
  }

  constructor() {
    super(...arguments);
    this.updateTask.perform();
  }

  @(task(function* () {
    while (true) {
      try {
        let { events } = yield this.ajax.request('/api/notifications');
        this.set('counter', events.filter(it => it.unread).length);
      } catch (error) {
        // ignore errors and try again in 60 sec
      }

      yield rawTimeout(60000);
    }
  }).drop())
  updateTask;
}
