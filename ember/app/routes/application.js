import Ember from 'ember';

export default Ember.Route.extend({
  account: Ember.inject.service(),
  intl: Ember.inject.service(),

  beforeModel() {
    this.get('intl').setLocale([Ember.$('meta[name=skylines-locale]').attr('content'), 'en']);
  },

  activate() {
    this._super(...arguments);

    let user = this.get('account.user');
    if (user) {
      this.get('raven').callRaven('setUserContext', user);
    }
  },
});
