import Component from '@ember/component';
import { computed } from '@ember/object';

export default class CirclingPerformanceTable extends Component {
  tagName = '';

  @findBy('perf', 'circlingDirection', 'left') left;
  @findBy('perf', 'circlingDirection', 'right') right;
  @findBy('perf', 'circlingDirection', 'mixed') mixed;
  @findBy('perf', 'circlingDirection', 'total') total;
}

function findBy(array, key, value) {
  return computed(`${array}.@each.${key}`, function () {
    return this[array].findBy(key, value);
  });
}
