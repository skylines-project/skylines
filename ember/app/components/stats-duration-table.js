import { mapBy, max, sum } from '@ember/object/computed';

import Component from '@glimmer/component';

export default class StatsDurationTable extends Component {
  @mapBy('args.years', 'duration') durations;
  @max('durations') max;
  @sum('durations') sum;
}
