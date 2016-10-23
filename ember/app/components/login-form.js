import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  session: Ember.inject.service(),

  classNameBindings: ['inline::panel-body'],

  inline: false,
  error: null,

  loginTask: task(function * () {
    let { email, password } = this.getProperties('email', 'password');

    try {
      yield this.get('session').authenticate('authenticator:cookie', email, password);
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
