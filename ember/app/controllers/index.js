import Ember from 'ember';

export default Ember.Controller.extend({
  account: Ember.inject.service(),

  notificationsURL: Ember.computed('account.user', function() {
    return this.get('account.user') ? '/notifications' : '/timeline';
  }),
});
