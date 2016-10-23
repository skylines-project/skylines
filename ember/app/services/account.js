import Ember from 'ember';

export default Ember.Service.extend({
  session: Ember.inject.service(),
  sessionData: Ember.computed.alias('session.data.authenticated.settings'),

  user: Ember.computed('sessionData.{id,name}', function() {
    let sessionData = this.get('sessionData');
    if (sessionData) {
      return Ember.getProperties(sessionData, 'id', 'name');
    }
  }),

  club: Ember.computed.alias('sessionData.club'),
});
