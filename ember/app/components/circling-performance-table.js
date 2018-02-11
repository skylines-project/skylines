import Component from '@ember/component';
import { findBy } from 'ember-awesome-macros/array';
import raw from 'ember-macro-helpers/raw';

export default Component.extend({
  left: findBy('perf', raw('circlingDirection'), raw('left')),
  right: findBy('perf', raw('circlingDirection'), raw('right')),
  mixed: findBy('perf', raw('circlingDirection'), raw('mixed')),
  total: findBy('perf', raw('circlingDirection'), raw('total')),
});
