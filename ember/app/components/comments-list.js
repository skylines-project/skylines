import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default Component.extend({
  tagName: '',
  account: service(),
  ajax: service(),
  addCommentText: '',

  addCommentTask: task(function*() {
    let id = this.flightId;
    let text = this.addCommentText;
    let user = this.get('account.user');

    yield this.ajax.request(`/api/flights/${id}/comments`, { method: 'POST', json: { text } });

    this.set('addCommentText', '');
    this.comments.pushObject({ text, user });
  }).drop(),
});
