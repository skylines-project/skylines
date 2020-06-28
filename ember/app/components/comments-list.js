import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default class CommentsList extends Component {
  tagName = '';

  @service account;
  @service ajax;

  addCommentText = '';

  @(task(function* () {
    let id = this.flightId;
    let text = this.addCommentText;
    let user = this.get('account.user');

    yield this.ajax.request(`/api/flights/${id}/comments`, { method: 'POST', json: { text } });

    this.set('addCommentText', '');
    this.comments.pushObject({ text, user });
  }).drop())
  addCommentTask;
}
