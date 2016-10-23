import Ember from 'ember';

export default Ember.Controller.extend({
  account: Ember.inject.service(),
  session: Ember.inject.service(),
});
