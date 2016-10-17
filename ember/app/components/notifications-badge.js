import Ember from 'ember';
import { task, timeout } from 'ember-concurrency';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),

  tagName: 'span',
  classNames: ['badge'],
  classNameBindings: ['hasNotifications:badge-warning'],

  counter: 0,
  hasNotifications: Ember.computed.gt('counter', 0),

  counterText: Ember.computed('counter', function() {
    let counter = this.get('counter');
    return (counter > 10) ? '10+' : counter;
  }),

  didInsertElement() {
    this._super(...arguments);
    this.get('updateCounterTask').perform();
  },

  updateCounterTask: task(function * () {
    // eslint-disable-next-line no-constant-condition
    while (true) {
      let { events } = yield this.get('ajax').request('/notifications');
      this.set('counter', events.filter(it => it.unread).length);
      yield timeout(60000);
    }
  }).drop(),
});
