import Ember from 'ember';

export default Ember.Route.extend({
  account: Ember.inject.service(),
  ajax: Ember.inject.service(),

  model() {
    let userId = this.get('account.user.id');
    if (userId) {
      return this.get('ajax').request('/api/settings');
    }
  },
});
