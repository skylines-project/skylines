import Component from '@ember/component';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  tagName: '',

  codeLower: safeComputed('code', code => code.toLowerCase()),
});
