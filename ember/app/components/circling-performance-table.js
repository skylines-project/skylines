import { computed } from '@ember/object';
import Component from '@glimmer/component';

export default class CirclingPerformanceTable extends Component {
  @findBy('perf', 'circlingDirection', 'left') left;
  @findBy('perf', 'circlingDirection', 'right') right;
  @findBy('perf', 'circlingDirection', 'mixed') mixed;
  @findBy('perf', 'circlingDirection', 'total') total;
}

function findBy(array, key, value) {
  return computed(`${array}.@each.${key}`, function () {
    return this.args[array]?.findBy(key, value);
  });
}
