import Ember from 'ember';

import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
  tagName: '',

  codeLower: safeComputed('code', code => code.toLowerCase()),
});
