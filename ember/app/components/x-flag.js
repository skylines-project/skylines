import Ember from 'ember';

import safeComputed from '../computed/safe-computed';

export default Ember.Component.extend({
  tagName: '',

  codeLower: safeComputed('code', code => code.toLowerCase()),
});
