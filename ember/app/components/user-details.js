import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

import safeComputed from '../computed/safe-computed';

export default class UserDetails extends Component {
  tagName = '';

  @service account;
  @service ajax;

  @safeComputed('account.user.id', 'user.id', (accountId, userId) => accountId && accountId === userId)
  editable;

  @(task(function* () {
    let userId = this.get('user.id');
    yield this.ajax.request(`/api/users/${userId}/follow`);
    this.set('user.followed', true);
    this.incrementProperty('user.followers');
  }).drop())
  followTask;

  @(task(function* () {
    let userId = this.get('user.id');
    yield this.ajax.request(`/api/users/${userId}/unfollow`);
    this.set('user.followed', false);
    this.decrementProperty('user.followers');
  }).drop())
  unfollowTask;
}
