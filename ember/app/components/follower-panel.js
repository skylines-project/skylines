import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { task } from 'ember-concurrency';

export default Component.extend({
  account: service(),
  ajax: service(),

  followTask: task(function * () {
    let userId = this.get('follower.id');
    yield this.get('ajax').request(`/api/users/${userId}/follow`);
    this.set('follower.currentUserFollows', true);
  }).drop(),

  unfollowTask: task(function * () {
    let userId = this.get('follower.id');
    yield this.get('ajax').request(`/api/users/${userId}/unfollow`);
    this.set('follower.currentUserFollows', false);
  }).drop(),
});
