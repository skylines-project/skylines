import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { task } from 'ember-concurrency';

export default Component.extend({
  account: service(),
  session: service(),

  tagName: '',

  logoutTask: task(function * () {
    yield this.get('session').invalidate();
  }).drop(),
});
