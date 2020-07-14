import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { inject as service } from '@ember/service';

export default class PinButton extends Component {
  @service pinnedFlights;

  tagName = '';

  @computed('pinnedFlights.pinned.[]', 'flightId')
  get pinned() {
    return this.pinnedFlights.pinned.includes(this.flightId);
  }

  @action toggle() {
    this.pinnedFlights.toggle(this.flightId);
  }
}
