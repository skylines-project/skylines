import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  account: Ember.inject.service(),
  ajax: Ember.inject.service(),

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
