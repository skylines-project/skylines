import { mapBy, max, sum } from '@ember/object/computed';

import Component from '@glimmer/component';

export default class StatsFlightsTable extends Component {
  @mapBy('args.years', 'flights') flights;
  @max('flights') max;
  @sum('flights') sum;
}
