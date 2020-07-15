import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default class FollowerPanel extends Component {
  tagName = '';

  @service account;
  @service ajax;

  @(task(function* () {
    let userId = this.get('follower.id');
    yield this.ajax.request(`/api/users/${userId}/follow`);
    this.set('follower.currentUserFollows', true);
  }).drop())
  followTask;

  @(task(function* () {
    let userId = this.get('follower.id');
    yield this.ajax.request(`/api/users/${userId}/unfollow`);
    this.set('follower.currentUserFollows', false);
  }).drop())
  unfollowTask;
}
