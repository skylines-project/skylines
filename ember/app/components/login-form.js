import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default Component.extend({
  tagName: '',

  session: service(),

  inline: false,
  error: null,

  loginTask: task(function*() {
    let { email, password } = this;

    try {
      yield this.session.authenticate('authenticator:oauth2', email, password);
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
