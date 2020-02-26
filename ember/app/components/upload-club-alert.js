import Component from '@ember/component';
import { alias, or, equal, not } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  account: service(),
  transitionTo() {},

  joinTask: task(function*() {
    this.set('showNoClubModal', false);
    this.transitionTo('settings/club');
  }).drop(),

});
