import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  account: Ember.inject.service(),
  ajax: Ember.inject.service(),

  addCommentText: '',

  addCommentTask: task(function * () {
    let id = this.get('flightId');
    let text = this.get('addCommentText');
    let user = this.get('account.user');

    yield this.get('ajax').request(`/flights/${id}/comments`, { method: 'POST', json: { text } });

    this.set('addCommentText', '');
    this.get('comments').pushObject({ text, user });
  }).drop(),
});
