import Ember from 'ember';

export default Ember.Route.extend({
  account: Ember.inject.service(),

  activate() {
    this._super(...arguments);

    let user = this.get('account.user');
    if (user) {
      this.get('raven').callRaven('setUserContext', user);
    }
  },
});
