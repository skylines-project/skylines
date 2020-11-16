import { action, computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@glimmer/component';

export default class PinButton extends Component {
  @service pinnedFlights;

  @computed('pinnedFlights.pinned.[]', 'args.flightId')
  get pinned() {
    return this.pinnedFlights.pinned.includes(this.args.flightId);
  }

  @action toggle() {
    this.pinnedFlights.toggle(this.args.flightId);
  }
}
