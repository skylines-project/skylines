import { inject as service } from '@ember/service';
import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

import { task } from 'ember-concurrency';

export default class CommentsList extends Component {
  @service account;
  @service ajax;
  @service intl;
  @service notifications;

  @tracked addCommentText = '';

  @(task(function* (event) {
    event.preventDefault();

    let id = this.args.flightId;
    let text = this.addCommentText;
    let { user } = this.account;

    try {
      yield this.ajax.request(`/api/flights/${id}/comments`, { method: 'POST', json: { text } });
      this.addCommentText = '';
      this.args.comments.pushObject({ text, user });
    } catch (error) {
      this.notifications.error(this.intl.t('comment-error'));
    }
  }).drop())
  addCommentTask;
}
