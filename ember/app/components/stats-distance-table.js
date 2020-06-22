import { mapBy, max, sum } from '@ember/object/computed';
import Component from '@glimmer/component';

export default class StatsDistanceTable extends Component {
  @mapBy('args.years', 'distance') distances;
  @max('distances') max;
  @sum('distances') sum;
}
