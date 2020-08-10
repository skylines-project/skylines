import { action, computed } from '@ember/object';
import Component from '@glimmer/component';

export default class extends Component {
  @computed('args.{nearFlights.[],visibleFlights.[]}')
  get nearFlightsWithColors() {
    let { nearFlights, visibleFlights } = this.args;
    return nearFlights.map(it => {
      let id = it.flight.id;
      let visibleFlight = visibleFlights.findBy('id', id);

      return {
        color: visibleFlight ? visibleFlight.get('color') : undefined,
        flight: it.flight,
        times: it.times,
      };
    });
  }

  @action
  select(id) {
    this.args.onSelect(id);
  }
}
