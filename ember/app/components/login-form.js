import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { task } from 'ember-concurrency';

export default Component.extend({
  session: service(),

  classNameBindings: ['inline::panel-body'],

  inline: false,
  error: null,

  loginTask: task(function * () {
    let { email, password } = this;

    try {
      yield this.session.authenticate('authenticator:oauth2', email, password);
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
