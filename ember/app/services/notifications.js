import { computed } from '@ember/object';
import { gt } from '@ember/object/computed';
import Service, { inject as service } from '@ember/service';
import { task, timeout } from 'ember-concurrency';

export default Service.extend({
  ajax: service(),

  counter: 0,
  hasUnread: gt('counter', 0),

  counterText: computed('counter', function() {
    let counter = this.get('counter');
    return (counter > 10) ? '10+' : counter;
  }),

  init() {
    this._super(...arguments);
    this.get('updateTask').perform();
  },

  updateTask: task(function * () {
    // eslint-disable-next-line no-constant-condition
    while (true) {
      let { events } = yield this.get('ajax').request('/api/notifications');
      this.set('counter', events.filter(it => it.unread).length);
      yield timeout(60000);
    }
  }).drop(),
});
