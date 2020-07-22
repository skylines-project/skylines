import { action, computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@glimmer/component';

export default class PinStar extends Component {
  @service pinnedFlights;

  @computed('pinnedFlights.pinned.[]', 'args.flightId')
  get pinned() {
    return this.pinnedFlights.pinned.includes(this.args.flightId);
  }

  @action handleClick() {
    this.pinnedFlights.toggle(this.args.flightId);
  }
}
