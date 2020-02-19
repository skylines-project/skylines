import Component from '@ember/component';
import { alias, or, equal, not } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  account: service(),
  ajax: service(),
  transitionTo() {},


});
