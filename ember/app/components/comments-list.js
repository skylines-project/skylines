import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { task } from 'ember-concurrency';

export default Component.extend({
  account: service(),
  ajax: service(),

  addCommentText: '',

  addCommentTask: task(function * () {
    let id = this.get('flightId');
    let text = this.get('addCommentText');
    let user = this.get('account.user');

    yield this.get('ajax').request(`/api/flights/${id}/comments`, { method: 'POST', json: { text } });

    this.set('addCommentText', '');
    this.get('comments').pushObject({ text, user });
  }).drop(),
});
