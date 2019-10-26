import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  tagName: '',
  left: findBy('perf', 'circlingDirection', 'left'),
  right: findBy('perf', 'circlingDirection', 'right'),
  mixed: findBy('perf', 'circlingDirection', 'mixed'),
  total: findBy('perf', 'circlingDirection', 'total'),
});

function findBy(array, key, value) {
  return computed(`${array}.@each.${key}`, function() {
    return this[array].findBy(key, value);
  });
}
