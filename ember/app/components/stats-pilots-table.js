import { mapBy, max, readOnly } from '@ember/object/computed';
import Component from '@glimmer/component';

export default class StatsPilotsTable extends Component {
  @mapBy('args.years', 'pilots') pilots;
  @max('pilots') max;
  @readOnly('args.sumPilots') sum;
}
